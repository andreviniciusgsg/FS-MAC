#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import pmt
import numpy as np 
import time
import thread
from oct2py import octave as oc

class ml_decision(gr.basic_block):
	"""
	docstring for block ml_decision
	"""

	def __init__(self, is_coord, alpha, filename, oct_path):
		gr.basic_block.__init__(self, name="ml_decision", in_sig=None, out_sig=None)

		# Variables
		self.is_coord = is_coord;
		self.alpha = alpha;
		self._filename = filename;
		self._oct_path = oct_path;
		self.max = self.act_protocol = self.sensor_1 = self.sensor_2 = self.sensor_3 = self.sensor_4 = self.sensor_5 = None;

		# Input ports
		self.message_port_register_in(pmt.intern("max in"));
		self.set_msg_handler(pmt.intern("max in"), self.handle_max);

		self.message_port_register_in(pmt.intern("act protocol in"));
		self.set_msg_handler(pmt.intern("act protocol in"), self.handle_act_protocol);

		self.message_port_register_in(pmt.intern("sensor 1 in"));
		self.set_msg_handler(pmt.intern("sensor 1 in"), self.handle_sensor_1);
		
		self.message_port_register_in(pmt.intern("sensor 2 in"));
		self.set_msg_handler(pmt.intern("sensor 2 in"), self.handle_sensor_2);

		self.message_port_register_in(pmt.intern("sensor 3 in"));
		self.set_msg_handler(pmt.intern("sensor 3 in"), self.handle_sensor_3);

		self.message_port_register_in(pmt.intern("sensor 4 in"));
		self.set_msg_handler(pmt.intern("sensor 4 in"), self.handle_sensor_4);

		self.message_port_register_in(pmt.intern("sensor 5 in"));
		self.set_msg_handler(pmt.intern("sensor 5 in"), self.handle_sensor_5);

		# Output ports
		self.message_port_register_out(pmt.intern("out"));
		
		self.start_decision_block();

	def start_decision_block(self):
		if self.is_coord:
			try:
				print "Coordinator mode."
				thread.start_new_thread(self.coord_loop, ("thread 1", 10));
			except:
				print "Error while initializing thread on coordinator.";
		else:
			print "Normal mode."

	# This is related to the parameter we want to maximize
	def handle_max(self, msg):
		if self.is_coord:
			thr = pmt.to_float(msg);
			if not np.isnan(thr):
				if self.max == None:
					self.max = thr;
				else:
					self.max = thr*self.alpha + (1 - self.alpha)*self.max;
				
	def handle_act_protocol(self, msg):
		self.act_protocol = pmt.to_uint64(msg);
		if self.act_protocol == 1:
			print "Active protocol: CSMA";
		elif self.act_protocol == 2:
			print "Active protocol: TDMA";

	# This sensor is responsible for number of nodes.
	def handle_sensor_1(self, msg): 
		non = pmt.to_uint64(msg);
		if not np.isnan(non):
			if self.sensor_1 == None:
				self.sensor_1 = non;
			else:
				self.sensor_1 = non*self.alpha + (1 - self.alpha)*self.sensor_1;

	# This sensor is responsible for latency.
	def handle_sensor_2(self, msg):
		if self.is_coord:
			latency = pmt.to_float(msg);
			if not np.isnan(latency):
				if self.sensor_2 == None:
					self.sensor_2 = latency;
				else:
					self.sensor_2 = latency*self.alpha + (1 - self.alpha)*self.sensor_2;
		else:
			self.message_port_pub(pmt.intern("out"), msg);

	# This sensor is responsible for RNP.
	def handle_sensor_3(self, msg):
		if self.is_coord:
			rnp = pmt.to_float(msg);
			if not np.isnan(rnp):
				if self.sensor_3 == None:
					self.sensor_3 = rnp;
				else:
					self.sensor_3 = rnp*self.alpha + (1 - self.alpha)*self.sensor_3;

	# This sensor is responsible for SNR.
	def handle_sensor_4(self, msg):
		if self.is_coord:
			snr = pmt.to_float(msg);
			if not np.isnan(snr):
				if self.sensor_4 == None:
					self.sensor_4 = snr;
				else:
					self.sensor_4 = snr*self.alpha + (1 - self.alpha)*self.sensor_4;

	def handle_sensor_5(self, msg):
		print "Nothing on this sensor";

	def coord_loop(self, thread_name, sleep_time):
		f = open(self._filename, 'a', 0);
		oct_path = self._oct_path;

		print self._oct_path;
		oc.addpath(self._oct_path);

		while True:
			time.sleep(sleep_time); # In seconds.

			if self.act_protocol != None and self.max != None and self.sensor_1 != None and self.sensor_2 != None and self.sensor_3 != None and self.sensor_4 != None:
				s = str(self.act_protocol) + "\t" + str(self.max) + "\t" + str(self.sensor_1) + "\t" + str(self.sensor_2) + "\t" + str(self.sensor_3) + "\t" + str(self.sensor_4) + "\n";
				f.write(s);

				result = oc.select_protocol(self._filename, self.act_protocol, self.max);

				if result == 1:
					csma = 100.0;
					tdma = 0.0;
				elif result == 2:
					csma = 0.0;
					tdma = 100.0;

				pmt_dict = pmt.make_dict();

				if csma > tdma:
					pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));
					pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
				else:
					pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
					pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));

				self.message_port_pub(pmt.intern('out'), pmt_dict);

		f.close();
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

class ml_decision(gr.basic_block):
	"""
	docstring for block ml_decision
	"""

	def __init__(self, is_coord):
		gr.basic_block.__init__(self, name="ml_decision", in_sig=None, out_sig=None)

		# Variables
		self.is_coord = is_coord;
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
				self.max = thr;

	def handle_act_protocol(self, msg):
		self.act_protocol = pmt.to_uint64(msg);

	# This sensor is responsible for number of nodes.
	def handle_sensor_1(self, msg): 
		non = pmt.to_uint64(msg);
		if not np.isnan(non):
			self.sensor_1 = non;
			print "Number of nodes = " + str(self.sensor_1);

	# This sensor is responsible for latency.
	def handle_sensor_2(self, msg):
		if self.is_coord:
			latency = pmt.to_float(msg);
			if not np.isnan(latency):
				self.sensor_2 = latency;
				print "Latency = " + str(self.sensor_2);
		else:
			self.message_port_pub(pmt.intern("out"), msg);

	# This sensor is responsible for RNP.
	def handle_sensor_3(self, msg):
		print msg;
		if self.is_coord:
			rnp = pmt.to_float(msg);
			if not np.isnan(rnp):
				self.sensor_3 = rnp;

	def handle_sensor_4(self, msg):
		print "Nothing on this sensor";

	def handle_sensor_5(self, msg):
		print "Nothing on this sensor";

	def coord_loop(self, thread_name, sleep_time):
		while True:
			time.sleep(sleep_time); # In seconds.

			print "Number of nodes = " + str(self.sensor_1) + "\nLatency = " + str(self.sensor_2) + "\nRNP = " + str(self.sensor_3) + "\nThroughput = " + str(self.max);

			csma = 100.0;
			tdma = 0.0;

			pmt_dict = pmt.make_dict();

			if csma > tdma:
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
			else:
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));
			
			self.message_port_pub(pmt.intern('out'), pmt_dict);
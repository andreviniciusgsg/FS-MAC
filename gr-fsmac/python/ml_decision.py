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
from sklearn import svm
from sklearn import linear_model as lin
from sklearn.neighbors import KNeighborsRegressor as knn
from sklearn import tree as dt
from sklearn.neural_network import MLPRegressor as nnet
from sklearn.ensemble import GradientBoostingRegressor as gbe

class ml_decision(gr.basic_block):
	"""
	docstring for block ml_decision
	"""
	# Machine Learning model:
	# 0: none, use CSMA
	# 1: none, use TDMA
	# 2: linear svm
	# 3: svm
	# 4: nusvm


	# Aggregation list:
	# 0: none
	# 1: moving average (alpha)
	# 2: summation
	# 3: max
	# 4: min

	def __init__(self, ml_model, is_coord, alpha, filename, training_file,
			aggr1, aggr2, aggr3, aggr4, aggr5, aggr_max, periodicity):
		gr.basic_block.__init__(self, name="ml_decision", in_sig=None, out_sig=None)

		# Variables
		self._ml_model = ml_model;
		self.is_coord = is_coord;
		self.alpha = alpha;
		self._filename = filename;
		self._training_file = training_file;
		self.max = self.act_protocol = self.sensor_1 = self.sensor_2 = self.sensor_3 = self.sensor_4 = self.sensor_5 = None;
		self._aggr1 = aggr1;
		self._aggr2 = aggr2;
		self._aggr3 = aggr3;
		self._aggr4 = aggr4;
		self._aggr5 = aggr5;
		self._aggr_max = aggr_max;
		self._period = periodicity;

		self._count_1 = self._count_2 = self._count_3 = self._count_4 = self._count_5 = 0;
		self._count_max = 0;
		
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
				thread.start_new_thread(self.coord_loop, ("thread 1", self._period));
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
					self._count_max = self._count_max + 1;
					self.max = thr;
				elif self._aggr_max == 0: # none
					self.max = thr;
				elif self._aggr_max == 1: # moving avg
					self.max = thr*self.alpha + (1 - self.alpha)*self.max;
				elif self._aggr_max == 2: # summation
					self.max = thr + self.max;
				elif self._aggr_max == 3: # max
					if thr > self.max:
						self.max = thr;
				elif self._aggr_max == 4: # min
					if thr < self.max:
						self.max = thr;
				elif self._aggr_max == 5: # simple avg
					self.max = self.max + thr;
					self._count_max = self._count_max + 1;
				
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
				self._count_1 = self._count_1 + 1;
				self.sensor_1 = non;
			elif self._aggr1 == 0: # none
				self.sensor_1 = 0;
			elif self._aggr1 == 1: # moving avg
				self.sensor_1 = non*self.alpha + (1 - self.alpha)*self.sensor_1;
			elif self._aggr1 == 2: # summation
				self.sensor_1 = self.sensor_1 + non;
			elif self._aggr1 == 3: # max
				if non > self.sensor_1:
					self.sensor_1 = non;
			elif self._aggr1 == 4: # min
				if non < self.sensor_1:
					self.sensor_1 = non;
			elif self._aggr1 == 5: # simple avg
				self.sensor_1 = self.sensor_1 + non;
				self._count_1 = self._count_1 + 1;

	# This sensor is responsible for latency.
	def handle_sensor_2(self, msg):
		if self.is_coord:
			latency = pmt.to_float(msg);
			if not np.isnan(latency):
				if self.sensor_2 == None:
					self._count_2 = self._count_2 + 1;
					self.sensor_2 = latency;
				elif self._aggr2 == 0: # none
					self.sensor_2 = latency;
				elif self._aggr2 == 1: # moving avg
					self.sensor_2 = latency*self.alpha + (1 - self.alpha)*self.sensor_2;
				elif self._aggr2 == 2: # summation
					self.sensor_2 = latency + self.sensor_2;
				elif self._aggr2 == 3: # max
					if latency > self.sensor_2:
						self.sensor_2 = latency;
				elif self._aggr2 == 4: # min
					if latency < self.sensor_2:
						self.sensor_2 = latency;
				elif self._aggr2 == 5: # simple avg
					self.sensor_2 = self.sensor_2 + latency;
					self._count_2 = self._count_2 + 1;
		else:
			self.message_port_pub(pmt.intern("out"), msg);

	# This sensor is responsible for RNP.
	def handle_sensor_3(self, msg):
		if self.is_coord:
			rnp = pmt.to_float(msg);
			if not np.isnan(rnp):
				if self.sensor_3 == None:
					self._count_3 = self._count_3 + 1;
					self.sensor_3 = rnp;
				elif self._aggr3 == 0: # none
					self.sensor_3 = rnp;
				elif self._aggr3 == 1: # moving avg
					self.sensor_3 = rnp*self.alpha + (1 - self.alpha)*self.sensor_3;
				elif self._aggr3 == 2: # summation
					self.sensor_3 = rnp + self.sensor_3;
				elif self._aggr3 == 3: # max
					if rnp > self.sensor_3:
						self.sensor_3 = rnp;
				elif self._aggr3 == 4: # min
					if rnp < self.sensor_3:
						self.sensor_3 = rnp;
				elif self._aggr3 == 5: # simple avg
					self.sensor_3 = self.sensor_3 + rnp;
					self._count_3 = self._count_3 + 1;

	# This sensor is responsible for SNR.
	def handle_sensor_4(self, msg):
		if self.is_coord:
			snr = pmt.to_float(msg);
			if not np.isnan(snr):
				if self.sensor_4 == None:
					self._count_4 = self._count_4 + 1;
					self.sensor_4 = snr;
				elif self._aggr4 == 0: # none
					self.sensor_4 = snr;
				elif self._aggr4 == 1: # moving avg
					self.sensor_4 = snr*self.alpha + (1 - self.alpha)*self.sensor_4;
				elif self._aggr4 == 2: # summation
					self.sensor_4 = snr + self.sensor_4;
				elif self._aggr4 == 3: # max
					if snr > self.sensor_4:
						self.sensor_4 = snr;
				elif self._aggr4 == 4: # min
					if snr < self.sensor_4:
						self.sensor_4 = snr;
				elif self._aggr4 == 5: # simple avg
					self.sensor_4 = self.sensor_4 + snr;
					self._count_4 = self._count_4 + 1;

	def handle_sensor_5(self, msg):
		print "Nothing on this sensor";

	def coord_loop(self, thread_name, sleep_time):
		d = np.loadtxt(self._training_file, delimiter="\t");
		f = open(self._filename, 'a', 0);

		x1 = [];
		x2 = [];

		y1 = [];
		y2 = [];

		for aux in d:
			if aux[0] == 1:
				y1.append(aux[1]);
				x1.append(list(aux[2:len(aux)]));
			elif aux[0] == 2:
				y2.append(aux[1]);
				x2.append(list(aux[2:len(aux)]));

		# Normalization
		x1 = np.array(x1);
		x2 = np.array(x2);
		y1 = np.array(y1);
		y2 = np.array(y2);

		u1 = np.arange(len(x1[0,:]))*0;
		s1 = np.arange(len(x1[0,:]))*0;
		u2 = np.arange(len(x2[0,:]))*0;
		s2 = np.arange(len(x2[0,:]))*0;

		for i in range(0, len(u1)):
			u1[i] = np.mean(x1[:,i]);
			s1[i] = np.max(x1[:,i]);
			u2[i] = np.mean(x2[:,i]);
			s2[i] = np.mean(x2[:,i]);

			if s1[i] == 0:
				s1[i] = 1;
			if s2[i] == 0:
				s2[i] = 1;

			x1[:,i] = (u1[i] - x1[:,i])/s1[i];
			x2[:,i] = (u2[i] - x2[:,i])/s2[i];

		csma = 0.0;
		tdma = 0.0;

		# Machine Learning models if not none (0 or 1)
		if self._ml_model != 0 and self._ml_model != 1 and self._ml_model != 2:
			if self._ml_model == 3:
				prot1 = lin.LinearRegression();
				prot2 = lin.LinearRegression();
			elif self._ml_model == 4:
				prot1 = svm.LinearSVR(random_state=0);
				prot2 = svm.LinearSVR(random_state=0);
			elif self._ml_model == 5:
				prot1 = svm.SVR();
				prot2 = svm.SVR();
			elif self._ml_model == 6:
				prot1 = svm.NuSVR(C=1.0, nu=0.1);
				prot2 = svm.NuSVR(C=1.0, nu=0.1);
			elif self._ml_model == 7:
				prot1 = knn(n_neighbors=2);
				prot2 = knn(n_neighbors=2);
			elif self._ml_model == 8:
				prot1 = dt.DecisionTreeRegressor();
				prot2 = dt.DecisionTreeRegressor();
			elif self._ml_model == 9:
				prot1 = nnet(max_iter=100000);
				prot2 = nnet(max_iter=100000);
			elif self._ml_model == 10:
				prot1 = gbe();
				prot2 = gbe();

			prot1.fit(x1, y1);
			prot2.fit(x2, y2);
		# No Machine Learning model, either pure CSMA or pure TDMA.
		elif self._ml_model == 0:
			csma = 100.0;
			tdma = 0.0;
		elif self._ml_model == 1:
			csma = 0.0;
			tdma = 100.0;

		tolerance = 1.1; # 10% tolerance.

		while True:
			time.sleep(sleep_time); # In seconds.

			if self.act_protocol != None and self.max != None and self.sensor_1 != None and self.sensor_2 != None and self.sensor_3 != None and self.sensor_4 != None:
				
				# if aggr is simple avg
				if self._aggr_max == 5:
					self.max = self.max/self._count_max;
				if self._aggr1 == 5:
					self.sensor_1 = self.sensor_1/self._count_1;
				if self._aggr2 == 5:
					self.sensor_2 = self.sensor_2/self._count_2;
				if self._aggr3 == 5:
					self.sensor_3 = self.sensor_3/self._count_3;
				if self._aggr4 == 5:
					self.sensor_4 = self.sensor_4/self._count_4;
				if self._aggr5 == 5:
					self.sensor_5 = self.sensor_5/self._count_5;

				s = str(self.act_protocol) + "\t" + str(self.max) + "\t" + str(self.sensor_1) + "\t" + str(self.sensor_2) + "\t" + str(self.sensor_3) + "\t" + str(self.sensor_4) + "\n";
				f.write(s);

				if self._ml_model != 0 and self._ml_model != 1 and self._ml_model != 2:
					_x1 = np.array([self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4]);
					_x2 = np.array([self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4]);
					for i in range(0, len(u1)):
						_x1[i] = (u1[i] - _x1[i])/s1[i];
						_x2[i] = (u2[i] - _x2[i])/s2[i];

					pred1 = float(prot1.predict([_x1]));
					pred2 = float(prot2.predict([_x2]));

					# A change only occurs when a prediction is 10% higher than current protocol prediction
					if self.act_protocol == 1:
						if pred2 >= tolerance*pred1:
							csma = 0.0;
							tdma = 100.0;
						else:
							csma = 100.0;
							tdma = 0.0;
					elif self.act_protocol == 2:
						if pred1 >= tolerance*pred2:
							csma = 100.0;
							tdma = 0.0;
						else:
							csma = 0.0;
							tdma = 100.0;
				# FS-MAC fuzzy logic
				elif self._ml_model == 2:
					csma = float(self.calculate_csma_adaptability(self.sensor_1, self.sensor_2));
					tdma = float(self.calculate_tdma_adaptability(self.sensor_1, self.sensor_2));
					print "CSMA = " + str(csma) + ", TDMA = " + str(tdma);

			else:
				print "Some counters are incomplete!";

			# Resetting counters	
			self.sensor_1 = self.sensor_2 = self.sensor_3 = self.sensor_4 = self.sensor_5 = self.max = None;
			self._count_1 = self._count_2 = self._count_3 = self._count_4 = self._count_5 = 0;
			self._count_max = 0;

			pmt_dict = pmt.make_dict();

			if csma > tdma:
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
			else:
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(1), pmt.cons(pmt.from_uint64(2), pmt.from_double(tdma)));
				pmt_dict = pmt.dict_add(pmt_dict, pmt.from_uint64(2), pmt.cons(pmt.from_uint64(1), pmt.from_double(csma)));

			self.message_port_pub(pmt.intern('out'), pmt_dict);

		f.close();




#############################################
#############################################
## GOD HELPS US! This is for FS-MAC legacy ##
#############################################
#############################################

	def calculate_tdma_adaptability(self, sens1_value, sens2_value):
		#if senders is higth AND data is higth then TDMA adaptability is hight
		#if senders is low AND data is higth then TDMA adaptability is low
		tdma_low_pert_decimals = [0,10,20,30,40,50,60]
		tdma_hight_pert_decimals = [40,50,60,70,80,90,100]

		csma_low_pert_decimals = [0,10,20,30,40,50,60]
		csma_hight_pert_decimals = [40,50,60,70,80,90,100]

		#======= FUZZYFICATION PHASE =======#
		senders_fuzy_pert = self.senders_function(sens1_value);
		data_fuzzy_pert = self.data_function(sens2_value);
		#===================================#

		numerator = 0
		denominator = 0

		value_hight_adapt = 0
		value_low_adapt = 0

		list_low_adapts = []
		list_hight_adapts = []

		#======= EVALUATION OF RULES =======#
		#if senders is higth AND data is higth then TDMA adaptability is hight
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[1]:
			list_hight_adapts.append(senders_fuzy_pert[1])
		else:
			list_hight_adapts.append(data_fuzzy_pert[1])

		#if senders is low AND data is higth then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[1]:
			list_low_adapts.append(senders_fuzy_pert[0])
		else:
			list_low_adapts.append(data_fuzzy_pert[1])

		#if senders is higth AND data is low then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[0]:
			list_low_adapts.append(senders_fuzy_pert[1])
		else:
			list_low_adapts.append(data_fuzzy_pert[0])

		#if senders is low AND data is low then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[0]:
			list_low_adapts.append(senders_fuzy_pert[0])
		else:
			list_low_adapts.append(data_fuzzy_pert[0])

		list_low_adapts.sort(reverse=True)
		list_hight_adapts.sort(reverse=True)

		value_low_adapt = list_low_adapts[0]
		value_hight_adapt = list_hight_adapts[0]
		#===================================#

		#====== DEFUZZYFICATION PHASE ======#
		for i in tdma_hight_pert_decimals:
			numerator = numerator + i*value_hight_adapt

		for j in tdma_low_pert_decimals:
			numerator = numerator + j*value_low_adapt

		denominator = denominator + len(tdma_hight_pert_decimals)*value_hight_adapt
		denominator = denominator + len(tdma_low_pert_decimals)*value_low_adapt

		if denominator == 0:
			denominator = 1

		adaptability_degree = numerator/denominator
		#===================================#

		return adaptability_degree


	def calculate_csma_adaptability(self, sens1_value, sens2_value):
		#if senders is higth AND data is higth then CSMA adaptability is low
		#if senders is low AND data is higth then CSMA adaptability is higth
		tdma_low_pert_decimals = [0,10,20,30,40,50,60]
		tdma_hight_pert_decimals = [40,50,60,70,80,90,100]

		csma_low_pert_decimals = [0,10,20,30,40,50,60]
		csma_hight_pert_decimals = [40,50,60,70,80,90,100]

		#======= FUZZYFICATION PHASE =======#
		senders_fuzy_pert = self.senders_function(sens1_value)
		data_fuzzy_pert = self.data_function(sens2_value)
		#===================================#

		numerator = 0
		denominator = 0

		value_hight_adapt = 0
		value_low_adapt = 0

		list_low_adapts = []
		list_hight_adapts = []

		#======= EVALUATION OF RULES =======#
		#if senders is higth AND data is higth then CSMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[1]:
			list_low_adapts.append(senders_fuzy_pert[1])
		else:
			list_low_adapts.append(data_fuzzy_pert[1])

		#if senders is low AND data is higth then CSMA adaptability is higth
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[1]:
			list_hight_adapts.append(senders_fuzy_pert[0])
		else:
			list_hight_adapts.append(data_fuzzy_pert[1])
		#===================================#

		#if senders is hight AND data is low then CSMA adaptability is higth
		if senders_fuzy_pert[1] < data_fuzzy_pert[0]:
			list_hight_adapts.append(senders_fuzy_pert[1])
		else:
			list_hight_adapts.append(data_fuzzy_pert[0])

		#if senders is low AND data is low then CSMA adaptability is hight
		if senders_fuzy_pert[0] < data_fuzzy_pert[0]:
			list_hight_adapts.append(senders_fuzy_pert[0])
		else:
			list_hight_adapts.append(data_fuzzy_pert[0])


		list_hight_adapts.sort(reverse=True)
		list_low_adapts.sort(reverse=True)

		value_hight_adapt = list_hight_adapts[0]
		value_low_adapt = list_low_adapts[0]


		#====== DEFUZZYFICATION PHASE ======#
		for i in csma_hight_pert_decimals:
			numerator = numerator + i*value_hight_adapt

		for j in csma_low_pert_decimals:
			numerator = numerator + j*value_low_adapt

		denominator = denominator + len(csma_hight_pert_decimals)*value_hight_adapt
		denominator = denominator + len(csma_low_pert_decimals)*value_low_adapt

		if denominator == 0:
			denominator = 1

		adaptability_degree = numerator/denominator
		#===================================#

		return adaptability_degree

	
	def senders_function(self, x):
		low_pert = 0;
		hight_pert = 0;

	#---- BEGIN COMMENT HERE FOR EXPERIMENT 2 ---
		if x >= 0 and x <= 1:
			low_pert = 100
		elif x > 1 and x < 2:
			low_pert = -100*x  + 200
		else:
			low_pert = 0
		
		if x >= 0 and x <= 1:
			hight_pert = 0
		elif x > 1 and x < 2:
			hight_pert = 100*x - 100
		else:
			hight_pert = 100
	#---- END COMMENT HERE FOR EXPERIMENT 2 ---

	#---- BEGIN UNCOMMENT HERE FOR EXPERIMENT 2 ---
		#if x >= 0 and x <= 2:
		#	low_pert = 100
		#elif x > 2 and x < 3:
		#	low_pert = -100*x + 300
		#else:
		#	low_pert = 0
		#
		#if x >= 0 and x <= 2:
		#	hight_pert = 0
		#elif x > 2 and x < 3:
		#	hight_pert = 100*x - 200
		#else:
		#	hight_pert = 100
	#---- END UNCOMMENT HERE FOR EXPERIMENT 2 ---

		return [low_pert, hight_pert]

	def data_function(self, x):
		low_pert = 0;
		hight_pert = 0;
	
	#---- BEGIN COMMENT HERE FOR EXPERIMENT 2 ---
		if self.act_protocol == 1:
			if x >= 0 and x <= 20:
				low_pert = 100
			elif x > 20 and x < 40:
				low_pert = -5*x  + 200
			else:
				low_pert = 0
		
			if x >= 0 and x <= 20:
				hight_pert = 0
			elif x > 20 and x < 40:
				hight_pert = 5*x - 100
			else:
				hight_pert = 100
		
		elif self.act_protocol == 2:
			if x >= 0 and x <= 20:
				low_pert = 100
			elif x > 20 and x < 25:
				low_pert = -20*x  + 500
			else:
				low_pert = 0
		
			if x >= 0 and x <= 20:
				hight_pert = 0
			elif x > 20 and x < 25:
				hight_pert = 20*x - 400
			else:
				hight_pert = 100
	#---- END COMMENT HERE FOR EXPERIMENT 2 ---

	#---- BEGIN UNCOMMENT HERE FOR EXPERIMENT 2 ---
		#if self.act_protocol == 1:
		#	if x >= 0 and x <= 35:
		#		low_pert = 100
		#	elif x > 35 and x < 55:
		#		low_pert = -5*x  + 275
		#	else:
		#		low_pert = 0
		#
		#	if x >= 0 and x <= 35:
		#		hight_pert = 0
		#	elif x > 35 and x < 55:
		#		hight_pert = 5*x - 175
		#	else:
		#		hight_pert = 100
		#
		#elif self.act_protocol == 2:
		#	if x >= 0 and x <= 23:
		#		low_pert = 100
		#	elif x > 23 and x < 26:
		#		low_pert = -33.33334*x  + 866.6667
		#	else:
		#		low_pert = 0
		#
		#	if x >= 0 and x <= 23:
		#		hight_pert = 0
		#	elif x > 23 and x < 26:
		#		hight_pert = 33.33334*x - 766.6667
		#	else:
		#		hight_pert = 100
	#---- END UNCOMMENT HERE FOR EXPERIMENT 2 ---

		return [low_pert, hight_pert]
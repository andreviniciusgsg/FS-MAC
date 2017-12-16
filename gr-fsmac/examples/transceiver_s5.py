#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IEEE 802.15.4 Transceiver using OQPSK PHY
# Generated: Sat Dec 16 11:46:12 2017
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from ieee802_15_4_oqpsk_phy import ieee802_15_4_oqpsk_phy  # grc-generated hier_block
from optparse import OptionParser
import fsmac
import ieee802_15_4
import pmt
import time
import toolkit


class transceiver_s5(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "IEEE 802.15.4 Transceiver using OQPSK PHY")

        ##################################################
        # Variables
        ##################################################
        self.gain = gain = 1
        self.freq = freq = 2.52e9

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(4000000)
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_normalized_gain(gain, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(4000000)
        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_normalized_gain(gain, 0)
        self.toolkit_cs_0 = toolkit.cs()
        self.logpwrfft_x_0 = logpwrfft.logpwrfft_c(
        	sample_rate=4e6,
        	fft_size=1024,
        	ref_scale=2,
        	frame_rate=30,
        	avg_alpha=0.01,
        	average=False,
        )
        self.ieee802_15_4_rime_stack_0 = ieee802_15_4.rime_stack(([129]), ([131]), ([132]), ([23,42]))
        self.ieee802_15_4_oqpsk_phy_0 = ieee802_15_4_oqpsk_phy()
        self.fsmac_tdma_0 = fsmac.tdma(5, 0, True, False)
        self.fsmac_snr_0 = fsmac.snr(1024, -70, 2)
        self.fsmac_ml_decision_0 = fsmac.ml_decision(2, False, 0.01, "", "", 3, 1, 3, 4, 0, 1, 20)
        self.fsmac_metrics_sensor_0 = fsmac.metrics_sensor(5, False)
        self.fsmac_latency_sensor_0 = fsmac.latency_sensor(False)
        self.fsmac_exchanger_0 = fsmac.exchanger(False)
        self.fsmac_csma_0 = fsmac.csma(5, 0, True)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, 1024)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_SERVER", "", "52001", 10000, False)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"), 5)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.ieee802_15_4_rime_stack_0, 'bcin'))    
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.ieee802_15_4_rime_stack_0, 'bcin'))    
        self.msg_connect((self.fsmac_csma_0, 'app out'), (self.fsmac_exchanger_0, 'p1_app in'))    
        self.msg_connect((self.fsmac_csma_0, 'ctrl out'), (self.fsmac_exchanger_0, 'p1_ctrl in'))    
        self.msg_connect((self.fsmac_csma_0, 'pdu out'), (self.fsmac_exchanger_0, 'p1_mac in'))    
        self.msg_connect((self.fsmac_csma_0, 'request cs'), (self.toolkit_cs_0, 'in_msg'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_app out'), (self.fsmac_csma_0, 'app in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_ctrl out'), (self.fsmac_csma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_mac out'), (self.fsmac_csma_0, 'pdu in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'dec out'), (self.fsmac_ml_decision_0, 'act protocol in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_app out'), (self.fsmac_tdma_0, 'app in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_ctrl out'), (self.fsmac_tdma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_mac out'), (self.fsmac_tdma_0, 'pdu in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'mac out'), (self.ieee802_15_4_oqpsk_phy_0, 'txin'))    
        self.msg_connect((self.fsmac_exchanger_0, 'app out'), (self.ieee802_15_4_rime_stack_0, 'fromMAC'))    
        self.msg_connect((self.fsmac_latency_sensor_0, 'dec out'), (self.fsmac_ml_decision_0, 'sensor 2 in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'send request'), (self.fsmac_csma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'data frame out'), (self.fsmac_exchanger_0, 'mac in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'rnp out'), (self.fsmac_ml_decision_0, 'sensor 3 in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'snr out'), (self.fsmac_ml_decision_0, 'sensor 4 in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'thr out'), (self.fsmac_ml_decision_0, 'max in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'non out'), (self.fsmac_ml_decision_0, 'sensor 1 in'))    
        self.msg_connect((self.fsmac_metrics_sensor_0, 'send request'), (self.fsmac_tdma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_ml_decision_0, 'out'), (self.fsmac_exchanger_0, 'dec in'))    
        self.msg_connect((self.fsmac_snr_0, 'snr out'), (self.fsmac_csma_0, 'snr in'))    
        self.msg_connect((self.fsmac_snr_0, 'snr out'), (self.fsmac_tdma_0, 'snr in'))    
        self.msg_connect((self.fsmac_tdma_0, 'app out'), (self.fsmac_exchanger_0, 'p2_app in'))    
        self.msg_connect((self.fsmac_tdma_0, 'ctrl out'), (self.fsmac_exchanger_0, 'p2_ctrl in'))    
        self.msg_connect((self.fsmac_tdma_0, 'pdu out'), (self.fsmac_exchanger_0, 'p2_mac in'))    
        self.msg_connect((self.ieee802_15_4_oqpsk_phy_0, 'rxout'), (self.fsmac_latency_sensor_0, 'pdu in'))    
        self.msg_connect((self.ieee802_15_4_oqpsk_phy_0, 'rxout'), (self.fsmac_metrics_sensor_0, 'frame in'))    
        self.msg_connect((self.ieee802_15_4_rime_stack_0, 'bcout'), (self.blocks_socket_pdu_0_0, 'pdus'))    
        self.msg_connect((self.ieee802_15_4_rime_stack_0, 'toMAC'), (self.fsmac_exchanger_0, 'app in'))    
        self.msg_connect((self.toolkit_cs_0, 'out_msg'), (self.fsmac_csma_0, 'cs in'))    
        self.connect((self.blocks_vector_to_stream_0, 0), (self.fsmac_snr_0, 0))    
        self.connect((self.blocks_vector_to_stream_0, 0), (self.toolkit_cs_0, 0))    
        self.connect((self.ieee802_15_4_oqpsk_phy_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.logpwrfft_x_0, 0), (self.blocks_vector_to_stream_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.ieee802_15_4_oqpsk_phy_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.logpwrfft_x_0, 0))    

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0.set_normalized_gain(self.gain, 0)
        	
        self.uhd_usrp_source_0.set_normalized_gain(self.gain, 0)
        	

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_sink_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)


def main(top_block_cls=transceiver_s5, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()

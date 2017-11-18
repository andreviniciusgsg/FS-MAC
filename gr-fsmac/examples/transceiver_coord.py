#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IEEE 802.15.4 Transceiver using OQPSK PHY
# Generated: Sat Nov 18 12:47:44 2017
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from ieee802_15_4_oqpsk_phy import ieee802_15_4_oqpsk_phy  # grc-generated hier_block
from optparse import OptionParser
import es
import foo
import fsmac
import ieee802_15_4
import metrics_ZigBee
import pmt
import time
import uhdgps
import wx


class transceiver_coord(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="IEEE 802.15.4 Transceiver using OQPSK PHY")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.gain = gain = 60
        self.freq = freq = 2480000000

        ##################################################
        # Blocks
        ##################################################
        _gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_gain_sizer,
        	value=self.gain,
        	callback=self.set_gain,
        	label='gain',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_gain_sizer,
        	value=self.gain,
        	callback=self.set_gain,
        	minimum=1,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.Add(_gain_sizer)
        self._freq_chooser = forms.radio_buttons(
        	parent=self.GetWin(),
        	value=self.freq,
        	callback=self.set_freq,
        	label="Channel",
        	choices=[1000000 * (2400 + 5 * (i - 10)) for i in range(11, 37)],
        	labels=[i for i in range(11, 37)],
        	style=wx.RA_HORIZONTAL,
        )
        self.Add(self._freq_chooser)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=freq,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=4e6,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="FFT Plot",
        	peak_hold=False,
        )
        self.Add(self.wxgui_fftsink2_0.win)
        self.uhdgps_cpdu_average_power_0 = uhdgps.cpdu_average_power(-60)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(4000000)
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(4000000)
        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_gain(gain, 0)
        self.metrics_ZigBee_rnp_0 = metrics_ZigBee.rnp(1)
        self.ieee802_15_4_rime_stack_0 = ieee802_15_4.rime_stack(([129]), ([131]), ([132]), ([23,42]))
        self.ieee802_15_4_oqpsk_phy_0 = ieee802_15_4_oqpsk_phy()
        self.fsmac_tdma_0 = fsmac.tdma(1, 2, True, True)
        self.fsmac_sens_num_senders_0 = fsmac.sens_num_senders()
        self.fsmac_ml_decision_0 = fsmac.ml_decision(True)
        self.fsmac_latency_sensor_0 = fsmac.latency_sensor(True)
        self.fsmac_exchanger_0 = fsmac.exchanger(True)
        self.fsmac_csma_0 = fsmac.csma(1, 2, True)
        self.foo_wireshark_connector_0 = foo.wireshark_connector(127, False)
        self.es_trigger_sample_timer_0 = es.trigger_sample_timer(gr.sizeof_gr_complex, int(1000), 2, int(4000000), 512 )
        self.es_sink_0 = es.sink(1*[gr.sizeof_gr_complex],8,64,0,2,0)
        self.es_handler_pdu_0 = es.es_make_handler_pdu(es.es_handler_print.TYPE_C32)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_SERVER", "", "52001", 10000, False)
        self.blocks_pdu_remove_0 = blocks.pdu_remove(pmt.intern("es::event_buffer"))
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.intern("12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"), 5e3)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, "/home/gnuradio/temp/output_802.15", False)
        self.blocks_file_sink_0.set_unbuffered(False)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.ieee802_15_4_rime_stack_0, 'bcin'))    
        self.msg_connect((self.blocks_pdu_remove_0, 'pdus'), (self.fsmac_csma_0, 'cs in'))    
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.ieee802_15_4_rime_stack_0, 'bcin'))    
        self.msg_connect((self.es_handler_pdu_0, 'pdus_out'), (self.uhdgps_cpdu_average_power_0, 'cpdus'))    
        self.msg_connect((self.es_trigger_sample_timer_0, 'sample_timer_event'), (self.es_handler_pdu_0, 'handle_event'))    
        self.msg_connect((self.es_trigger_sample_timer_0, 'which_stream'), (self.es_sink_0, 'schedule_event'))    
        self.msg_connect((self.fsmac_csma_0, 'app out'), (self.fsmac_exchanger_0, 'p1_app in'))    
        self.msg_connect((self.fsmac_csma_0, 'ctrl out'), (self.fsmac_exchanger_0, 'p1_ctrl in'))    
        self.msg_connect((self.fsmac_csma_0, 'pdu out'), (self.fsmac_exchanger_0, 'p1_mac in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'mac out'), (self.foo_wireshark_connector_0, 'in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_app out'), (self.fsmac_csma_0, 'app in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_ctrl out'), (self.fsmac_csma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p1_mac out'), (self.fsmac_csma_0, 'pdu in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'dec out'), (self.fsmac_ml_decision_0, 'act protocol in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_app out'), (self.fsmac_tdma_0, 'app in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_ctrl out'), (self.fsmac_tdma_0, 'ctrl in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'p2_mac out'), (self.fsmac_tdma_0, 'pdu in'))    
        self.msg_connect((self.fsmac_exchanger_0, 'app out'), (self.ieee802_15_4_rime_stack_0, 'fromMAC'))    
        self.msg_connect((self.fsmac_exchanger_0, 'mac out'), (self.metrics_ZigBee_rnp_0, 'frame in'))    
        self.msg_connect((self.fsmac_latency_sensor_0, 'dec out'), (self.fsmac_ml_decision_0, 'sensor 2 in'))    
        self.msg_connect((self.fsmac_ml_decision_0, 'out'), (self.fsmac_exchanger_0, 'dec in'))    
        self.msg_connect((self.fsmac_sens_num_senders_0, 'dec out'), (self.fsmac_ml_decision_0, 'sensor 1 in'))    
        self.msg_connect((self.fsmac_tdma_0, 'app out'), (self.fsmac_exchanger_0, 'p2_app in'))    
        self.msg_connect((self.fsmac_tdma_0, 'ctrl out'), (self.fsmac_exchanger_0, 'p2_ctrl in'))    
        self.msg_connect((self.fsmac_tdma_0, 'pdu out'), (self.fsmac_exchanger_0, 'p2_mac in'))    
        self.msg_connect((self.ieee802_15_4_oqpsk_phy_0, 'rxout'), (self.fsmac_exchanger_0, 'mac in'))    
        self.msg_connect((self.ieee802_15_4_oqpsk_phy_0, 'rxout'), (self.fsmac_latency_sensor_0, 'pdu in'))    
        self.msg_connect((self.ieee802_15_4_oqpsk_phy_0, 'rxout'), (self.fsmac_sens_num_senders_0, 'pdu in'))    
        self.msg_connect((self.ieee802_15_4_rime_stack_0, 'bcout'), (self.blocks_socket_pdu_0_0, 'pdus'))    
        self.msg_connect((self.ieee802_15_4_rime_stack_0, 'toMAC'), (self.fsmac_exchanger_0, 'app in'))    
        self.msg_connect((self.metrics_ZigBee_rnp_0, 'frame out'), (self.ieee802_15_4_oqpsk_phy_0, 'txin'))    
        self.msg_connect((self.uhdgps_cpdu_average_power_0, 'cpdus'), (self.blocks_pdu_remove_0, 'pdus'))    
        self.connect((self.es_trigger_sample_timer_0, 0), (self.es_sink_0, 0))    
        self.connect((self.foo_wireshark_connector_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.ieee802_15_4_oqpsk_phy_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.es_trigger_sample_timer_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.ieee802_15_4_oqpsk_phy_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_fftsink2_0, 0))    

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self._gain_slider.set_value(self.gain)
        self._gain_text_box.set_value(self.gain)
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)
        	
        self.uhd_usrp_source_0.set_gain(self.gain, 0)
        	

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self._freq_chooser.set_value(self.freq)
        self.uhd_usrp_sink_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.wxgui_fftsink2_0.set_baseband_freq(self.freq)


def main(top_block_cls=transceiver_coord, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable real-time scheduling."

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()

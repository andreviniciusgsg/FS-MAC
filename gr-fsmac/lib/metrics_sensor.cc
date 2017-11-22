/* -*- c++ -*- */
/* 
 * Copyright 2017 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.	If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <fsmac/metrics_sensor.h>
#include <pmt/pmt.h>
#include <boost/thread.hpp>
#include <time.h>

#define RNP_REQUEST 5
#define THROUGHPUT_REQUEST 6
#define SNR_REQUEST 7

using namespace gr::fsmac;

class metrics_sensor_impl : public metrics_sensor {
	private:
		// Message ports
		pmt::pmt_t msg_port_rx_in;

		pmt::pmt_t msg_port_rnp_out;
		pmt::pmt_t msg_port_snr_out;
		pmt::pmt_t msg_port_throughput_out;
		pmt::pmt_t msg_port_request_metrics;
		pmt::pmt_t msg_port_data_frame_out;

		// Parameters
		uint8_t pr_periodicity;
		bool pr_is_coord;

		// Threads
		boost::shared_ptr<gr::thread::thread> thread;

		// Variables
		float pr_rnp_sum, pr_thr_sum, pr_snr_sum;

	public:

		metrics_sensor_impl(uint8_t periodicity, bool is_coord)
		: block("metrics_sensor",
					gr::io_signature::make(0, 0, 0),
					gr::io_signature::make(0, 0, 0)),
					pr_periodicity(periodicity),
					pr_is_coord(is_coord) {

			msg_port_rnp_out = pmt::mp("rnp out");
			msg_port_snr_out = pmt::mp("snr out");
			msg_port_throughput_out = pmt::mp("thr out");
			msg_port_data_frame_out = pmt::mp("data frame out");
			msg_port_request_metrics = pmt::mp("send request");
			msg_port_rx_in = pmt::mp("frame in");

			message_port_register_in(msg_port_rx_in);
			set_msg_handler(msg_port_rx_in, boost::bind(&metrics_sensor_impl::rx_in, this, _1));

			message_port_register_out(msg_port_rnp_out);
			message_port_register_out(msg_port_snr_out);
			message_port_register_out(msg_port_throughput_out);
			message_port_register_out(msg_port_data_frame_out);
			message_port_register_out(msg_port_request_metrics);

			pr_rnp_sum = 0;
			pr_snr_sum = 0;
			pr_thr_sum = 0;
		}

		~metrics_sensor_impl(void) {}

		bool start() {
			thread = boost::shared_ptr<gr::thread::thread> (new gr::thread::thread(boost::bind(&metrics_sensor_impl::request_metrics, this)));
		
			return block::start();
		}

		void rx_in(pmt::pmt_t frame) {
			if(pr_is_coord) {

				pmt::pmt_t cdr;

				if(pmt::is_pair(frame)) {
					cdr = pmt::cdr(frame);
				} else {
					assert(false);
				}

				size_t len = pmt::blob_length(cdr);

				if(len < 1 && len != 6) return; // Frame is too short!

				char* pkg = (char*) pmt::blob_data(cdr);
				pkg[len - 1] = '\0';
				len = len - 1;
				pkg = (char*) pmt::blob_data(cdr);
				uint16_t crc = crc16(pkg, len);

				/* RNP */
				if(crc == 0 and pkg[0] == 0x41 and pkg[9] == 'G') {
					int payload_len = len - 10;
					char payload[payload_len + 1];

					for(int i = 0; i < payload_len; i++) {
						payload[i] = pkg[10 + i];
					}
					payload[payload_len] = '\0';

					std::string str(payload);

					double rnp;
					std::istringstream s(str);
					s >> rnp;

					pr_rnp_sum += rnp;
				}

				else if(crc == 0 and pkg[0] == 0x41 and pkg[9] == 'I') {
					int payload_len = len - 10;
					char payload[payload_len + 1];

					for(int i = 0; i < payload_len; i++) {
						payload[i] = pkg[10 + i];
					}
					payload[payload_len] = '\0';

					std::string str(payload);

					double snr;
					std::istringstream s(str);
					s >> snr;

					pr_snr_sum += snr;
				}

				/* Throughput */
				else if(crc == 0 and pkg[0] == 0x41 and pkg[9] == 'H') {
					int payload_len = len - 10;
					char payload[payload_len + 1];

					for(int i = 0; i < payload_len; i++) {
						payload[i] = pkg[10 + i];
					}
					payload[payload_len] = '\0';

					std::string str(payload);

					double thr;
					std::istringstream s(str);
					s >> thr;

					pr_thr_sum += thr;
				}

				/* Data frame */
				else {
					message_port_pub(msg_port_data_frame_out, frame);
				}
			}
		}

		void request_metrics() {
			pmt::pmt_t command;
			while(true) {
				usleep(pr_periodicity*1000000); // Sleep for x seconds.
				// RNP
				command = pmt::from_uint64(RNP_REQUEST);
				message_port_pub(msg_port_request_metrics, command);
				usleep(pr_periodicity); // Short interval between requests.

				// SNR
				command = pmt::from_uint64(SNR_REQUEST);
				message_port_pub(msg_port_request_metrics, command);
				usleep(pr_periodicity); // Short interval between requests.

				// Throughput
				command = pmt::from_uint64(THROUGHPUT_REQUEST);
				message_port_pub(msg_port_request_metrics, command);
				usleep(pr_periodicity); // Short interval between requests.

				// Other metric

				// Send result to Decision block
				usleep(pr_periodicity*1000000*.2); // To make sure data arrives before sending to Decision block.
				message_port_pub(msg_port_rnp_out, pmt::from_float(pr_rnp_sum));
				message_port_pub(msg_port_snr_out, pmt::from_float(pr_snr_sum));
				message_port_pub(msg_port_throughput_out, pmt::from_float(pr_thr_sum)); // Fps (Frames per second)

				// Reset counters.
				pr_rnp_sum = 0;
				pr_snr_sum = 0;
				pr_thr_sum = 0;
			}
		}

		uint16_t crc16(char *buf, int len) {
			uint16_t crc = 0;

			for (int i = 0; i < len; i++) {
				for (int k = 0; k < 8; k++) {
					int input_bit = (!!(buf[i] & (1 << k)) ^ (crc & 1));
					crc = crc >> 1;
					if (input_bit) {
						crc ^= (1 << 15);
						crc ^= (1 << 10);
						crc ^= (1 << 3);
					}
				}
			}
			return crc;
		}
};

metrics_sensor::sptr
metrics_sensor::make(uint8_t periodicity, bool is_coord) {
	return gnuradio::get_initial_sptr
		(new metrics_sensor_impl(periodicity, is_coord));
}
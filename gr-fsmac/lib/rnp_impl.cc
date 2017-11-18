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
#include <pmt/pmt.h>
#include "rnp_impl.h"

using namespace gr::fsmac;

class rnp_impl : public rnp
{
	private:
		// Parameters
		uint16_t pr_periodicity;

		// Input message ports
		pmt::pmt_t msg_port_frame_in = pmt::mp("frame in");

		// Output message ports
		pmt::pmt_t msg_port_frame_out = pmt::mp("frame out");

	public:
		rnp_impl(uint16_t periodicity):block("rnp",	
			gr::io_signature::make(0, 0, 0),
			gr::io_signature::make(0, 0, 0)),
			pr_periodicity(periodicity) {

				message_port_register_in(msg_port_frame_in);
				set_msg_handler(msg_port_frame_in, boost::bind(&rnp_impl::frame_in, this, _1));

				message_port_register_out(msg_port_frame_out);			
		}

		~rnp_impl() {}

		void frame_in(pmt::pmt_t frame) {
			message_port_pub(msg_port_frame_out, frame);
			std::cout << "A frame has just arrived. Frame bypassed." << std::endl;
		}
};

rnp::sptr
rnp::make(uint16_t periodicity) {
	return gnuradio::get_initial_sptr(new rnp_impl(periodicity));
}
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
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */


#ifndef INCLUDED_FSMAC_METRICS_SENSOR_H
#define INCLUDED_FSMAC_METRICS_SENSOR_H

#include <fsmac/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace fsmac {

    /*!
     * \brief <+description of block+>
     * \ingroup fsmac
     *
     */
    class FSMAC_API metrics_sensor : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<metrics_sensor> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of fsmac::metrics_sensor.
       *
       * To avoid accidental use of raw pointers, fsmac::metrics_sensor's
       * constructor is in a private implementation
       * class. fsmac::metrics_sensor::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t periodicity, bool is_coord);
    };

  } // namespace fsmac
} // namespace gr

#endif /* INCLUDED_FSMAC_METRICS_SENSOR_H */


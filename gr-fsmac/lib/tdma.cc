/* -*- c++ -*- */
/* 
 * Copyright 2016 <Jefferson Rayneres Silva Cordeiro {jeff@dcc.ufmg.br} - DCC/UFMG>.
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <fsmac/tdma.h>
#include <gnuradio/io_signature.h>
#include <gnuradio/block_detail.h>
//#include <list>
#include <cstdlib>

#include <iostream>
#include <iomanip>
#include <boost/thread.hpp>
#include <boost/date_time.hpp>
#include <stdio.h>
#include <stddef.h>
#include <sys/time.h>
#include <string.h>
#include <time.h>
#include <chrono>

#include "SendPackage.h"
#include "MyList.h"
#include "MyListLat.h"

using namespace gr::fsmac;

class tdma_impl : public tdma {
    //    std::list<SendPackage*> sendList;
    MyList& sendList = MyList::Instance();
    std::list<SendPackage*> commandList;
    //    MyList& mylist = MyList::Instance();
    std::list<char*> requestComAddrList;
    boost::shared_ptr<gr::thread::thread> execCoord;
    boost::shared_ptr<gr::thread::thread> waitToComputeTb;
    boost::shared_ptr<gr::thread::thread> waitMyComSlot;

    std::list<double> latencyListForSensor;

    boost::mutex mut3;

    long int ack_slot = 2; //2
    long int data_slot = 4; //4
    long int aloc_slot = 2; //2
    long int guard_time = 2; //1

    long int com_slot = data_slot + ack_slot;

    //    long int slotTime = 50;

    short max_retr = 5;
    bool comm_ready = false;
    boost::condition_variable cond3;

    int state = 0;
    //    bool is_cordinator = false;
    bool canCompute = false;
    long int timeToStart = 60000;
    bool exchanging = true;
    float latencyAv = 0.0;
    int latency_counter = 0;
    bool answer_sending = false;
    long int num_fsmac_packs = 0;

    //Endereço MAC local. Os endereços possuem 2 bytes, assim, essas duas 
    //variáveis representam apenas um endereço. Para testes, esse endereço deve 
    //ser mudado para cada máquina. Deve-se lembrar de manter a coerência com 
    //os endereços de outras máquinas atribuidos na função start() e com a 
    //chamada da função generate_mac() feita na função app_in().
    char mac_addr_1; // = 0x41;
    char mac_addr_2; // = 0xe8;

    //Endereço de broadcast
    char addr_bc_1 = 0xff;
    char addr_bc_2 = 0xff;

    //Endereços de outras máquinas para simulações
    char addr0[2];
    char addr1[2];
    char addr2[2];
    char addr3[2];
    char addr4[2];
    char addr5[2];
    char addr6[2];

    int addrs_len = 7;

    //array que vai conter os endereços das outras máquinas
    char* addrs[7];

    boost::shared_ptr<gr::thread::thread> waitAloc;
    boost::condition_variable condAloc;
    boost::mutex mutAloc;
    long int alocTime;
    bool timeToAlocFinished = false;
    bool waitingAck = false;

    long int numPackConfirmados = 0;
    long int numRetransmissoes = 0;
    long int numPackEnviados = 0;

    struct timeval t1, t2;
    struct timeval myComT1, myComT2;
    struct timeval myComT3, myComT4;
    std::list<double> listaLatencias;
    //MyListLat& listaLatencias = MyListLat::Instance();

    double elapsedTime = 0;

public:

#define TYPE_UNKNOWN 0
#define TYPE_DATA 1
#define TYPE_ACK 2
#define TYPE_BEACON_SYNC 3
#define TYPE_BEACON_ALOC 4
#define TYPE_REQUEST_COM 5

#define STATE_SYNC 0
#define STATE_ALOC 1
#define STATE_COMUNICATION 2

#define EXCHANGE_COMMAND_SEND_INFO 0
#define EXCHANGE_COMMAND_INFO_SENT 1
#define EXCHANGE_COMMAND_STOP 2
#define EXCHANGE_COMMAND_DONE 3
#define LATENCY_SENSOR_COMMAND_SEND 4
#define RNC_COMMAND 5
#define THROUGHPUT_COMMAND 6
#define SNR_COMMAND 7

#define dout d_debug && std::cout

    tdma_impl(int mac_addr, int dest_node, bool debug, bool is_coord) :
    block("tdma",
    gr::io_signature::make(0, 0, 0),
    gr::io_signature::make(0, 0, 0)),
    d_msg_offset(0),
    d_seq_nr(0),
    d_debug(debug),
    is_coordinator(is_coord),
    d_num_packet_errors(0),
    d_num_packets_received(0) {

        indexDestNode = dest_node;
        indexLocalMac = mac_addr;

        //        sendList = mylist.getList();

        message_port_register_in(pmt::mp("app in"));
        set_msg_handler(pmt::mp("app in"), boost::bind(&tdma_impl::app_in, this, _1));
        message_port_register_in(pmt::mp("pdu in"));
        set_msg_handler(pmt::mp("pdu in"), boost::bind(&tdma_impl::mac_in, this, _1));
        message_port_register_in(pmt::mp("ctrl in"));
        set_msg_handler(pmt::mp("ctrl in"), boost::bind(&tdma_impl::ctrl_in, this, _1));
        message_port_register_in(pmt::mp("snr in"));
        set_msg_handler(pmt::mp("snr in"), boost::bind(&tdma_impl::snr_in, this, _1));

        message_port_register_out(pmt::mp("app out"));
        message_port_register_out(pmt::mp("pdu out"));
        message_port_register_out(pmt::mp("ctrl out"));

        d_rnp_rtx = 0;
        d_rnp_nr_pkts = 0;
        d_confirmed_pkts = 0;
        d_snr = 0;
        d_start_time = std::chrono::high_resolution_clock::now();
    }

    ~tdma_impl(void) {
    }

    void snr_in(pmt::pmt_t msg) {
        float snr = pmt::to_float(msg);
        if(snr < 0) snr = 0;
        d_snr = snr;
    }

    void calculateLatencyAv() {
        float sum = 0.0;
        latency_counter = 0;
        long unsigned int tam_lista = latencyListForSensor.size();

//        std::list<double>::iterator it = latencyListForSensor.end();
//        while (it != latencyListForSensor.begin()) {
//            sum = sum + (*it);
//            latency_counter++;
//            it--;
//        }

        int index = 0;
        std::list<double>::iterator it = latencyListForSensor.begin();
        while (index < tam_lista) {
            sum = sum + (*it);
            latency_counter++;
            it++;
            index++;
        }

        latencyAv = sum / latency_counter;
        latencyListForSensor.clear();
    }

    void ctrl_in(pmt::pmt_t msg) {
        if (pmt::is_pair(msg)) {
            int command; // = pmt::to_uint64(msg);
            int new_protocol;

            pmt::pmt_t command_pmt = pmt::car(msg);
            pmt::pmt_t new_protocol_pmt = pmt::cdr(msg);

            command = pmt::to_uint64(command_pmt);
            new_protocol = pmt::to_uint64(new_protocol_pmt);

            char new_prot;

            if (new_protocol == 1) {
                new_prot = '1';
            } else if (new_protocol == 2) {
                new_prot = '2';
            }

            if (command == EXCHANGE_COMMAND_SEND_INFO) {
//                printf("TDMA: Recebeu comando de envio.\n");
                char commandFsmac[2];
                commandFsmac[1] = 0x01;

                char* request = (char*) malloc(sizeof (char)*1);
                request[0] = 'Z';

                char packRequest[256];
                char addr_d[2];
                addr_d[0] = addr_bc_1;
                addr_d[1] = addr_bc_2;

                generateControlFsmacPack(request, 0, new_prot, packRequest, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                pmt::pmt_t packReq = pmt::cons(pmt::PMT_NIL, pmt::make_blob(packRequest, control_pack_len));
                SendPackage* packageFsmac = new SendPackage(packReq, commandFsmac[1], false);

                comm_ready = true;
                commandList.push_back(packageFsmac);

                //                boost::unique_lock<boost::mutex> lock3(mut3);
                //
                //                while (comm_ready) {
                //                    cond3.wait(lock3);
                //                }
                //                
                //                lock3.unlock();

                if (new_protocol != 2) {                    
                    answer_sending = true;
                }
            }
        } else if (pmt::is_uint64(msg)) {
            int command = pmt::to_uint64(msg);

            if (command == EXCHANGE_COMMAND_STOP) {
//                printf("TDMA: Parar atuação\n");
                exchanging = true;
                pmt::pmt_t pack_list = pmt::make_dict();
                message_port_pub(pmt::mp("ctrl out"), pack_list);

            } else if (command == LATENCY_SENSOR_COMMAND_SEND) {
                calculateLatencyAv();

                if (latency_counter > 0) {

                    std::ostringstream ss;
                    ss << latencyAv;
                    std::string latency_str(ss.str());

                    //                    char latency_char[1024];
                    //                    strncpy(latency_char, latency_str.c_str(), sizeof (latency_char));
                    //                    latency_char[sizeof (latency_char) - 1] = 0;

                    char commandFsmac[2];
                    commandFsmac[1] = 0x01;

                    //                char* request = (char*) malloc(sizeof (char)*1);
                    //                request[0] = 'Z';

                    char packRequest[256];
                    char addr_d[2];
                    addr_d[0] = addr_bc_1;
                    addr_d[1] = addr_bc_2;

                    char comm = 'L';
                    //                    printf("TDMA: Gerando comando de latência\n");
                    //                    generateControlFsmacPack(latency_char, (int) (ssize_t) latency_str.length(), comm, packRequest, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                    std::stringstream ss2;
                    ss2 << latency_counter;
                    std::string latency_counter_str = ss2.str();

                    //                    char latency_counter_char[1024];
                    //                    strncpy(latency_counter_char, latency_counter_str.c_str(), sizeof (latency_counter_char));
                    //                    latency_counter_char[sizeof (latency_counter_char) - 1] = 0;

                    std::string couter_plus_av(latency_counter_str + "&" + latency_str);
                    int sizeCounterPlusAv = ((int) (ssize_t) latency_counter_str.length()) + ((int) (ssize_t) latency_str.length());

                    char couter_plus_av_char[1024];
                    strncpy(couter_plus_av_char, couter_plus_av.c_str(), sizeof (couter_plus_av_char));
                    couter_plus_av_char[sizeof (couter_plus_av_char) - 1] = 0;

                    generateControlFsmacPack(couter_plus_av_char, sizeCounterPlusAv, comm, packRequest, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                    //                    pmt::pmt_t latency_counter_blob = pmt::make_blob(latency_counter_char, (int) (ssize_t) latency_counter_str.length());

                    //                    pmt::pmt_t packReq = pmt::cons(latency_counter_blob, pmt::make_blob(packRequest, control_pack_len));
                    pmt::pmt_t packReq = pmt::cons(pmt::get_PMT_NIL(), pmt::make_blob(packRequest, control_pack_len));

                    SendPackage* packageFsmac = new SendPackage(packReq, commandFsmac[1], false);

 //                   pmt::print(packReq);

                    comm_ready = true;
                    commandList.push_back(packageFsmac);

                    //                    printf("TDMA: colocou pacote de latências na fila.\n");

                    //                    boost::unique_lock<boost::mutex> lock3(mut3);

                    //                    while (comm_ready) {
                    //                        cond3.wait(lock3);
                    //                    }

                    //                    printf("TDMA: Saiu do LOOP de envios\n");
                    //                    lock3.unlock();
                } 
            } else if(command == RNC_COMMAND) {

                std::cout << "Send RNP" << std::endl;

                float rnp;
                if(d_rnp_nr_pkts > 0) {
                   rnp = d_rnp_rtx/d_rnp_nr_pkts;
                } else {
                    rnp = 0;
                }

                d_rnp_rtx = 0; d_rnp_nr_pkts = 0;
                
                std::ostringstream ss;
                ss << rnp;
                std::string rnp_str(ss.str());

                char commandFsmac[2];
                commandFsmac[1] = 0x01;

                char pack_request[256];
                char addr_d[2];
                addr_d[0] = addr_bc_1;
                addr_d[1] = addr_bc_2;

                char comm = 'G';

                int size = (int) (ssize_t) rnp_str.length();

                char buff_char[1024];
                strncpy(buff_char, rnp_str.c_str(), sizeof(buff_char));
                buff_char[sizeof(buff_char) - 1] = 0;

                generateControlFsmacPack(buff_char, size, comm, pack_request, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                pmt::pmt_t pack = pmt::cons(pmt::get_PMT_NIL(), pmt::make_blob(pack_request, control_pack_len));

                SendPackage* pkg = new SendPackage(pack, commandFsmac[1], false);

                comm_ready = true;
                commandList.push_back(pkg);
            } else if(command == THROUGHPUT_COMMAND) {
                std::cout << "Send throughput" << std::endl;

                d_end_time = std::chrono::high_resolution_clock::now();
                float duration = (float) std::chrono::duration_cast<std::chrono::seconds>(d_end_time - d_start_time).count();
                float thr;

                if(duration > 0) {
                    thr = d_confirmed_pkts/duration; // KFps (kilo frames per second).
                } else {
                    thr = 0; // No time window to take measurement.
                }

                d_start_time = std::chrono::high_resolution_clock::now();
                d_confirmed_pkts = 0;

                std::ostringstream ss;
                ss << thr;
                std::string thr_str(ss.str());

                char commandFsmac[2];
                commandFsmac[1] = 0x01;

                char pack_request[256];
                char addr_d[2] = {addr_bc_1, addr_bc_2};

                char comm = 'H';

                int size = (int) (ssize_t) thr_str.length();

                char buff_char[1024];
                strncpy(buff_char, thr_str.c_str(), sizeof(buff_char));
                buff_char[sizeof(buff_char) - 1] = 0;

                generateControlFsmacPack(buff_char, size, comm, pack_request, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                pmt::pmt_t pack = pmt::cons(pmt::get_PMT_NIL(), pmt::make_blob(pack_request, control_pack_len));

                SendPackage* pkg = new SendPackage(pack, commandFsmac[1], false);

                comm_ready = true;
                commandList.push_back(pkg);
            } else if(command = SNR_COMMAND) {
                std::cout << "Send SNR" << std::endl;

                float snr = d_snr;

                std::ostringstream ss;
                ss << snr;
                std::string snr_str(ss.str());

                char commandFsmac[2];
                commandFsmac[1] = 0x01;

                char pack_request[256];
                char addr_d[2] = {addr_bc_1, addr_bc_2};

                char comm = 'I';

                int size = (int) (ssize_t) snr_str.length();

                char buff_char[1024];
                strncpy(buff_char, snr_str.c_str(), sizeof(buff_char));
                buff_char[sizeof(buff_char) - 1] = 0;

                generateControlFsmacPack(buff_char, size, comm, pack_request, EXCHANGE_COMMAND_SEND_INFO, addr_d);

                pmt::pmt_t pack = pmt::cons(pmt::get_PMT_NIL(), pmt::make_blob(pack_request, control_pack_len));

                SendPackage* pkg = new SendPackage(pack, commandFsmac[1], false);

                comm_ready = true;
                commandList.push_back(pkg);
            }
        } else if (pmt::is_dict(msg)) {
//            printf("TDMA: Recebeu fila para trocar protocolo CSMA.\n");

            pmt::pmt_t exch_command = pmt::from_uint64(EXCHANGE_COMMAND_DONE);
            message_port_pub(pmt::mp("ctrl out"), exch_command);
            exchanging = false;
            if (is_coordinator) {
                execCoord = boost::shared_ptr<gr::thread::thread>
                        (new gr::thread::thread(boost::bind(&tdma_impl::executeCoord, this)));
            }
        }
    }

    /**
     * Função que trata as entradas da conexão "pdu in". 
     * Recebe mensagens que contêm pacotes MAC
     * @param msg Mensagem com pacotes MAC (Dados ou acks)
     */
    void mac_in(pmt::pmt_t msg) {
        pmt::pmt_t blob;

        if (pmt::is_pair(msg)) {
            blob = pmt::cdr(msg);
        } else {
            assert(false);
        }

        size_t data_len = pmt::blob_length(blob);

        if (data_len < 12 && data_len != 6) {
            dout << "MAC: frame too short. Dropping!" << std::endl;
            return;
        }

        char* recPackage = (char*) malloc(sizeof (char)*data_len);
        recPackage[data_len - 1] = '\0';
        data_len = data_len - 1;

        recPackage = (char*) pmt::blob_data(blob);
        uint16_t crc = crc16(recPackage, data_len);

        if (crc) {
            //printf("CRC calculado no recebimento: %hu\n",crc);           
            d_num_packet_errors++;
            dout << "MAC: wrong crc. Dropping packet!" << std::endl;
            //            printPack(recPackage, data_len);
            //            printPackChar(recPackage, data_len);
            printf("\n");
            //            message_port_pub(pmt::mp("app out"), pmt::cons(pmt::PMT_NIL, blob));
            return;
        } else {

            switch (getPackType(recPackage)) {
                case TYPE_ACK:
                    std::cout << "ACK frame" << std::endl << std::flush;
                    handleAck(recPackage);
                    break;

                case TYPE_DATA:
                    std::cout << "Data frame" << std::endl << std::flush;
                    handleDataPack(recPackage, data_len);
                    break;

                case TYPE_BEACON_SYNC:
                    std::cout << "Sync frame" << std::endl << std::flush;
                    handleSyncBeacon(recPackage, data_len);
                    break;

                case TYPE_BEACON_ALOC:
                    std::cout << "Aloc frame" << std::endl << std::flush;
                    handleAlocBeacon(recPackage, data_len);
                    break;

                case TYPE_REQUEST_COM:
                    std::cout << "Request com frame" << std::endl << std::flush;
                    handleRequestCom(recPackage);
                    break;
                default:
                    std::cout << "Unknown frame" << std::endl << std::flush;
//                    printf("Unknown type pack");
                    printf(" ");
            }

        }

    }

    void printPack(char* pack, int data_len) {
        int j = 0;
        for (j = 0; j < data_len; j++) {
            printf("%x-", pack[j] & 0xff);
        }
        printf("\n");
    }

    void printPackChar(char* pack, int data_len) {
        int j = 0;
        for (j = 0; j < data_len; j++) {
            printf("%c-", pack[j]);
        }
        printf("\n");
    }

    void handleAlocBeacon(char* recPack, size_t data_len) {
        //        printf("HANDLE ALOC\n");
        if (state == STATE_ALOC && !is_coordinator) {

            state = STATE_COMUNICATION;
            //            printf("\nCOM\n");
            long int time = calculateAlocWaiting(recPack, data_len, TYPE_BEACON_ALOC);
            if (time != -1) {
                if (time > 0) {
                    boost::posix_time::millisec workTime(time);
                    boost::this_thread::sleep(workTime);
                }
                if (!exchanging) {
                    runSending();
                }

            }
        }
    }

    void handleSyncBeacon(char* recPack, size_t size) {
        if (!is_coordinator) {
            state = STATE_SYNC;
            //            printf("\nSYNC\n");

            char* request = (char*) malloc(sizeof (char)*1);

            if (!sendList.empty()) {
                request[0] = 'T';

                long int time = calculateSyncWaiting(recPack, size);
                int sizePack = (int) (ssize_t) size;

                if (time != -1) {
                    boost::posix_time::millisec workTime(time);
                    boost::this_thread::sleep(workTime);

                    char packRequest[256];
                    char addr_d[2];
                    addr_d[0] = recPack[7];
                    addr_d[1] = recPack[8];

                    generateControlPack(request, 0, packRequest, TYPE_REQUEST_COM, addr_d);

                    pmt::pmt_t packReq = pmt::cons(pmt::PMT_NIL, pmt::make_blob(packRequest, control_pack_len));
                    message_port_pub(pmt::mp("pdu out"), packReq);
                }
            }
        }

        state = STATE_ALOC;
        //        printf("\nALOC\n");
    }

    void handleDataPack(char* recPackage, size_t size) {
        if (state == STATE_COMUNICATION) {
            if ((mac_addr_1 != recPackage[7] || mac_addr_2 != recPackage[8]) &&
                    ((mac_addr_1 == recPackage[5] && mac_addr_2 == recPackage[6]) ||
                    addr_bc_1 == recPackage[5] && addr_bc_2 == recPackage[6])) {

                if (d_debug) {
                    printf("Recebeu pacote de dados %u\n", (unsigned char) recPackage[2]);
                }

                d_num_packets_received++;

                int data_len = (int) (ssize_t) size;

                pmt::pmt_t mac_payload = pmt::make_blob(recPackage + 10, data_len - 10 - 2);
                message_port_pub(pmt::mp("app out"), pmt::cons(pmt::PMT_NIL, mac_payload));

                //Só envia pacote ack se a mensagem recebida não for de broadcast                
                if (addr_bc_1 != recPackage[5] || addr_bc_2 != recPackage[6]) {
                    char dAck[6];
                    generateAck(recPackage, dAck);

                    pmt::pmt_t packAck = pmt::cons(pmt::PMT_NIL, pmt::make_blob(dAck, 6));
                    message_port_pub(pmt::mp("pdu out"), packAck);

                    if (d_debug) {
                        printf("Enviou pacote ack\n\n");
                    }
                }
            }
        }
    }

    void iniciaContagemLatencia() {
        gettimeofday(&myComT1, NULL);
    }

    void finalizaContagemLatencia() {
        gettimeofday(&myComT2, NULL);

        double timeCom = 0;

        timeCom = (myComT2.tv_sec - myComT1.tv_sec) * 1000.0; // sec to ms
        timeCom += (myComT2.tv_usec - myComT1.tv_usec) / 1000.0; // us to ms

        listaLatencias.push_back(timeCom);
        latencyListForSensor.push_back(timeCom);
        if (d_debug) {
            printf("Elapsed time: %f\n", timeCom);
        }
    }
    
    
    /**
     * Inicia a contagem de tempo para medição periódica 
     * de latência como sensoriamento para decisão de troca.
     */
    void iniciaContagemLatenciaParaSensor() {
        gettimeofday(&myComT3, NULL);
    }
    
    /**
     * Finaliza a contagem de tempo para medição periódica 
     * de latência como sensoriamento para decisão de troca.
     */
    void finalizaContagemLatenciaParaSensor() {
        gettimeofday(&myComT4, NULL);

        double timeCom = 0;

        timeCom = (myComT4.tv_sec - myComT3.tv_sec) * 1000.0; // sec to ms
        timeCom += (myComT4.tv_usec - myComT3.tv_usec) / 1000.0; // us to ms

        latencyListForSensor.push_back(timeCom);
        if (d_debug) {
            printf("Elapsed time sensor: %f\n", timeCom);
        }
    }

    void handleAck(char* recPack) {
        removePackAcked(recPack);
    }

    void handleRequestCom(char* recPack) {
        if (is_coordinator && state == STATE_ALOC) {
            if (recPack[9] == 'R') {
                char* addrCom = (char*) malloc(sizeof (char)*2);
                addrCom[0] = recPack[7];
                addrCom[1] = recPack[8];
                requestComAddrList.push_back(addrCom);
            }
        }
    }

    int getPackType(char* recPack) {
        if (isAckPack(recPack)) {
            return TYPE_ACK;
        } else if (recPack[9] == 'D') {
            return TYPE_DATA;
        } else if (recPack[9] == 'S') {
            return TYPE_BEACON_SYNC;
        } else if (recPack[9] == 'A') {
            return TYPE_BEACON_ALOC;
        } else if (recPack[9] == 'R') {
            return TYPE_REQUEST_COM;
        } else if (recPack[0] == 0x61) {
            return TYPE_DATA;
        } else {
            return TYPE_UNKNOWN;
        }
    }

    long int calculateAlocWaiting(char* recPack, size_t size, int packType) {
        bool slotPresent = false;
        int time = 0;
        int sizePack = (int) (ssize_t) size;
        int lastIndexAddr = sizePack - 4; //where the last addr STARTS
        int i = 0;

        for (i = 10; i <= lastIndexAddr; i = i + 2) {
            if (recPack[i] != mac_addr_1 || recPack[i + 1] != mac_addr_2) {

                time++;
            } else {
                slotPresent = true;
                break;
            }
        }

        if (slotPresent) {
            return (time * (com_slot + guard_time)) +guard_time;
        } else {
            return -1;
        }
    }

    long int calculateSyncWaiting(char* recPack, size_t size) {
        bool slotPresent = false;
        int time = 0;
        int sizePack = (int) (ssize_t) size;
        int lastIndexAddr = sizePack - 4; //where the last addr STARTS
        int i = 0;

        for (i = 10; i <= lastIndexAddr; i = i + 2) {
            if (recPack[i] != mac_addr_1 || recPack[i + 1] != mac_addr_2) {
                time++;
            } else {
                slotPresent = true;
                break;
            }
        }

        if (slotPresent) {
            return time * aloc_slot;
        } else {
            return -1;
        }
    }

    bool isAckPack(char* recPack) {
        bool isA = recPack[0] == 0x02;
        return isA;
    }

    /**
     * Marca o pacote como confirmado e diz que ele pode ser removido. Não 
     * remove o pacote da fila diretamente para evitar problemas de 
     * produtor/consumidor.
     */
    void removePackAcked(char* ackPack) {
        unsigned char packId;
        packId = ackPack[2];
        //        printf("TDMA: Entrou no remove\n");
        if (!sendList.empty() && waitingAck == true) {
            //            printf("TDMA: Passou pelo if\n");
            std::list<SendPackage*>::iterator it = sendList.begin();
            //        while (it != sendList.end()) {
            if ((*it)->getId() == packId) {
                SendPackage* packToRemove = *it;
                it++;
                sendList.remove(packToRemove);
                //                printf("TDMA: Removeu pacote\n");
                waitingAck = false;
                //                finalizaContagemLatencia();
                
                finalizaContagemLatenciaParaSensor();
                finalizaContagemLatencia();
                
                if (canCompute) {
                    numPackConfirmados++; d_confirmed_pkts++;
                }

                if (d_debug) {
                    printf("Package %u acked.\n\n", (unsigned char) ackPack[2]);
                }

                //                break;
            }
            //            it++;
            //        }
        }

    }

    /**
     * Função que trata a entrada da conexção "app in".
     */
    void app_in(pmt::pmt_t msg) {
        pmt::pmt_t blob;
        if (pmt::is_eof_object(msg)) {
            dout << "MAC: exiting" << std::endl;
            detail().get()->set_done(true);
            return;
        } else if (pmt::is_blob(msg)) {
            blob = msg;
        } else if (pmt::is_pair(msg)) {
            blob = pmt::cdr(msg);
        } else {
            dout << "MAC: unknown input" << std::endl;
            return;
        }

        //LOG printf("Preparando pacote para o endereco: %u%u\n\n", addr0[0], addr0[1]);

        //Neste caso, todos os pacotes estão sendo enviados para o endereço 
        //addr0, para melhorar os testes, este endereço poderia ser escolhido 
        //aleatoriamente entre os endereços disponíveis.
        generate_mac((const char*) pmt::blob_data(blob), pmt::blob_length(blob), addrs[indexDestNode]);
        pmt::pmt_t pack = pmt::cons(pmt::PMT_NIL, pmt::make_blob(d_msg, d_msg_len));


        SendPackage* package = new SendPackage(pack, d_msg[2], false);
        package->setTime(0);
        send(package);
    }

    /**
     * Esta função inicia o processo de envio da mensagem. Ela coloca o pacote 
     * na fila para envio, notifica a thread principal que há dados prontos para 
     * serem enviados.
     * 
     * A função que implementa essa espera é a executeM().
     */
    void send(SendPackage * pack) {
        if (sendList.size() < 100) {
            sendList.push_back(pack);
            //            mylist.push_back(pack);
            //            printf("Size List: %d\n", mylist.size());
        }
    }

    void waitToCompute() {
        boost::posix_time::millisec workTimeAloc(timeToStart);
        boost::this_thread::sleep(workTimeAloc);

        canCompute = true;
        
        listaLatencias.clear();
        
    }

    /**
     * Esta função sobrescreve a função nativa do GNU Radio que ativa o bloco. 
     * Foi necessário usá-la para iniciar a thread principal. 
     */
    bool start() {

        //Estes endereços estão sendo alocados manualmente para testes. Em um
        //cenário onde a rede funcione de forma completa, estes endereços são 
        //fornecidos por um nó de coordenação, que informa de tempos em tempos
        //quais são os nós presentes na rede.

        //        if(is_coordinator && !exchanging){
        execCoord = boost::shared_ptr<gr::thread::thread>
                (new gr::thread::thread(boost::bind(&tdma_impl::executeCoord, this)));
        //        }

        addr0[0] = 0x40;
        addr0[1] = 0xe8;

        addr1[0] = 0x41;
        addr1[1] = 0xe8;

        addr2[0] = 0x42;
        addr2[1] = 0xe8;

        addr3[0] = 0x43;
        addr3[1] = 0xe8;

        addr4[0] = 0x44;
        addr4[1] = 0xe8;

        addr5[0] = 0x45;
        addr5[1] = 0xe8;

        addr6[0] = 0x46;
        addr6[1] = 0xe8;

        addrs[0] = addr0;
        addrs[1] = addr1;
        addrs[2] = addr2;
        addrs[3] = addr3;
        addrs[4] = addr4;
        addrs[5] = addr5;
        addrs[6] = addr6;

        mac_addr_1 = addrs[indexLocalMac][0]; //mac_addr[0];
        mac_addr_2 = addrs[indexLocalMac][1]; //mac_addr[1];

        gettimeofday(&t1, NULL);

        return block::start();
    }

    bool stop() {

        if (is_coordinator) {
            execCoord->interrupt();
            //execCoord->join();
        }

        //waitToComputeTb->join();
        waitToComputeTb->interrupt();

        if (numPackEnviados != 0) {
            gettimeofday(&t2, NULL);

            // compute and print the elapsed time in millisec
            elapsedTime = (t2.tv_sec - t1.tv_sec) * 1000.0; // sec to ms
            elapsedTime += (t2.tv_usec - t1.tv_usec) / 1000.0; // us to ms
            long int finalTime = elapsedTime - timeToStart;
            printf("\n");
            std::cout << "RESULADOS_TDMA:" << std::endl;
            std::cout << "Tempo:" << finalTime << ":ms" << std::endl;
            std::cout << "Enviados:" << numPackEnviados << std::endl;
            std::cout << "Confirmados:" << numPackConfirmados << std::endl;
            std::cout << "Retransmissoes: " << numRetransmissoes << std::endl;
            std::cout << "pacotesFsmac:" << num_fsmac_packs << std::endl;
            std::cout << "VazaoPs: " << numPackConfirmados / (finalTime / 1000) << " pacotes/s" << std::endl;
            std::cout << "VazaoBs:" << numPackConfirmados * 110 / (finalTime / 1000) << " bytes/s" << std::endl;
            std::cout << "Taxa:" << double(numPackConfirmados) / numPackEnviados * 100 << " porcento" << std::endl;
            std::cout << "Latencias:"; // << finalTime/numPackConfirmados << " ms" << std::endl;

            std::list<double>::iterator it = listaLatencias.begin();
            while (it != listaLatencias.end()) {
                std::cout << (*it) << ";";
                it++;
            }
            }

        return block::stop();
    }

    void waitAlocTime() {

        boost::posix_time::millisec workTimeAloc(alocTime);
        boost::this_thread::sleep(workTimeAloc);

        timeToAlocFinished = true;
        condAloc.notify_all();
    }

    void executeCoord() {
        if (d_debug) {
            timeToStart = 1000;
        }
        waitToComputeTb = boost::shared_ptr<gr::thread::thread>
                (new gr::thread::thread(boost::bind(&tdma_impl::waitToCompute, this)));

        if (is_coordinator && !exchanging) {
            while (!exchanging) {
                state = STATE_SYNC;
                //                printf("\nSYNC\n");

                char seqSync[addrs_len * 2];
                int i = 0;
                for (i = 0; i < addrs_len; i++) {
                    seqSync[i * 2] = addrs[i][0];
                    seqSync[i * 2 + 1] = addrs[i][1];
                }

                char* syncPack = (char*) malloc(sizeof (char)*256);
                char dest[2];
                dest[0] = addr_bc_1;
                dest[1] = addr_bc_2;


                //                for(i=0; i<(addrs_len * 2); i++){
                //                    printf("%x ", seqSync[i] & 0xff);
                //                }

                int seqSyncSize = addrs_len * 2;

                generateControlPack(seqSync, seqSyncSize, syncPack, TYPE_BEACON_SYNC, dest);

                pmt::pmt_t syncPackPmt = pmt::cons(pmt::PMT_NIL, pmt::make_blob(syncPack, control_pack_len));
                message_port_pub(pmt::mp("pdu out"), syncPackPmt);

                state = STATE_ALOC;
                //                printf("\nALOC\n");
                alocTime = addrs_len * com_slot;

                boost::posix_time::millisec workTimeAloc(alocTime);
                boost::this_thread::sleep(workTimeAloc);

                bool coordCom = false;
                if ((!sendList.empty() || !commandList.empty()) && !exchanging) {
                    char localAddr[2];
                    localAddr[0] = mac_addr_1;
                    localAddr[1] = mac_addr_2;

                    requestComAddrList.push_back(localAddr);
                    coordCom = true;
                }

                int listSize = requestComAddrList.size();
                char* sequence = (char*) malloc(sizeof (char)* (listSize * 2));

                i = 0;
                std::list<char*>::iterator it = requestComAddrList.begin();

                while (it != requestComAddrList.end()) {
                    sequence[i * 2] = (*it)[0];
                    sequence[i * 2 + 1] = (*it)[1];
                    i++;
                    it++;
                }

                int seqAlocSize = requestComAddrList.size() * 2;
                char* alocPack = (char*) malloc(sizeof (char)*256);

                generateControlPack(sequence, seqAlocSize, alocPack, TYPE_BEACON_ALOC, dest);

                pmt::pmt_t alocPackPmt = pmt::cons(pmt::PMT_NIL, pmt::make_blob(alocPack, control_pack_len));
                message_port_pub(pmt::mp("pdu out"), alocPackPmt);

                state = STATE_COMUNICATION;
                //                printf("\nCOM\n");

                long int timeCom = ((requestComAddrList.size() - 1) * (com_slot + guard_time)) + guard_time;

                boost::posix_time::millisec workTimeCom(timeCom);
                boost::this_thread::sleep(workTimeCom);

                if (coordCom && !exchanging) {
                    runSending();
                }

                long int timeComCoord = com_slot + guard_time;

                boost::posix_time::millisec workTimeComCoord(timeComCoord);
                boost::this_thread::sleep(workTimeComCoord);

                requestComAddrList.clear();
            }
        }
    }

    void runSending() {
        //        printf("TDMA: Entrou na runSending()\n");

        if ((!sendList.empty() || !commandList.empty()) && !exchanging) {
            //printf("TDMA: Entrou no IF de envios FS-MAC\n");
            if (!commandList.empty()) {
                SendPackage* packToSend = commandList.front();
                sendPackageNow(packToSend);
                //printf("Enviou pacote FS-MAC\n");
                if (packToSend->getResends() == 2) {
                    //printf("FIM DO ENVIO DE PACOTES FS-MAC\n");
                    comm_ready = false;
                    commandList.pop_front();

                    if (answer_sending) {
                        pmt::pmt_t exch_command = pmt::from_uint64(EXCHANGE_COMMAND_INFO_SENT);
                        message_port_pub(pmt::mp("ctrl out"), exch_command);
                    }
                    answer_sending = false;
                }
            } else {
                SendPackage* packToSend = sendList.front();
                sendPackageNow(packToSend);
                if (packToSend->getCanRemove()) {
                    sendList.pop_front();
                }
            }

        }

    }

    /**
     * Envia de fato os pacotes e incrementa o número de reenvios.
     */
    bool sendPackageNow(SendPackage * pack) {
        pmt::pmt_t pmt_pack = pack->getPackage();

        //        size_t tamanho = pmt::blob_length(pmt::cdr(pmt_pack));
        //        char* sp = (char*) pmt::blob_data(pmt::cdr(pmt_pack));
        //        uint16_t crc = crc16(sp, tamanho - 1);
        // printf("CRC calculado no envio: %hu\n",crc);
        message_port_pub(pmt::mp("pdu out"), pmt_pack);
        //        pmt::print(pmt_pack);
        //        iniciaContagemLatencia();
        waitingAck = true;

        if (d_debug) {
            printf("TDMA: Enviou pacote dados %u\n", pack->getId());
        }

//        if (!comm_ready) {
//            iniciaContagemLatenciaParaSensor();
//        }

        if (!comm_ready) {
            if (pack->getResends() == 0) {
                if (canCompute) {
                    numPackEnviados++; d_rnp_nr_pkts++;
                }
                iniciaContagemLatencia();
                iniciaContagemLatenciaParaSensor();
            } else {
                if(canCompute){
                    numRetransmissoes++; d_rnp_rtx++;                
                }
            }
        } else if (comm_ready) {
            if (canCompute) {
                num_fsmac_packs++;
            }
        }

//        if (canCompute) {
//            if (!comm_ready) {
//                if (pack->getResends() == 0) {
//                    iniciaContagemLatencia();
//                    numPackEnviados++;
//                } else {
//                    numRetransmissoes++;
//                }
//            }else if(comm_ready){
//                num_fsmac_packs++;
//            }
//        }

        pack->increaseResends(max_retr);
        return true;
    }

    /**
     * Função da implementação original. Funciona bem, mas tem um problema de 
     * retorno, quando o crc falha, retorna true, no caso de sucesso, retorna 
     * false.
     * @param buf
     * @param len
     * @return 
     */
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

    void generateControlPack(char *buf, int bufSize, char* pack, int type, char* addr_dest) {
        int len = 0;
        char packFunc[1];

        int i = 0;

        if (type == TYPE_REQUEST_COM) {
            packFunc[0] = 'R';
        } else if (type == TYPE_BEACON_SYNC) {
            packFunc[0] = 'S';
        } else if (type == TYPE_BEACON_ALOC) {
            packFunc[0] = 'A';
        }

        char payload[bufSize + 1];
        payload[0] = packFunc[0];

        for (i = 0; i < bufSize; i++) {
            payload[i + 1] = buf[i];
        }

        if (bufSize > 0) {
            std::memcpy(payload + 1, buf, strlen(buf));
        }

        len = bufSize + 1; //payload size
        unsigned char packId;
        packId = d_seq_nr;

        pack[0] = 0x61;
        pack[1] = 0x88;

        // seq nr
        pack[2] = packId;

        pack[3] = 0xcd;
        pack[4] = 0xab;
        pack[5] = addr_dest[0];
        pack[6] = addr_dest[1];
        pack[7] = mac_addr_1;
        pack[8] = mac_addr_2;

        std::memcpy(pack + 9, payload, len);

        uint16_t crc = crc16(pack, len + 9);

        pack[ 9 + len] = crc & 0xFF;
        pack[10 + len] = crc >> 8;
        pack[11 + len] = 0x7f;

        control_pack_len = 9 + len + 3;

    }

    void generateControlFsmacPack(char *buf, int bufSize, char new_prot, char* pack, int type, char* addr_dest) {
        int len = 0;
        char packFunc[1];

        int i = 0;

        if (type == EXCHANGE_COMMAND_SEND_INFO) {
            packFunc[0] = new_prot;
        }

        char payload[bufSize + 1];
        payload[0] = packFunc[0];

        for (i = 0; i < bufSize; i++) {
            payload[i + 1] = buf[i];
        }

        if (bufSize > 0) {
            std::memcpy(payload + 1, buf, strlen(buf));
        }

        len = bufSize + 1; //payload size
        unsigned char packId;
        packId = d_seq_nr;

        pack[0] = 0x41;
        pack[1] = 0x88;

        // seq nr
        pack[2] = packId;

        pack[3] = 0xcd;
        pack[4] = 0xab;
        pack[5] = 0xff;
        pack[6] = 0xff;
        pack[7] = mac_addr_1;
        pack[8] = mac_addr_2;

        std::memcpy(pack + 9, payload, len);

        uint16_t crc = crc16(pack, len + 9);

        pack[ 9 + len] = crc & 0xFF;
        pack[10 + len] = crc >> 8;
        pack[11 + len] = 0x7f;

        control_pack_len = 9 + len + 3;

    }

    /**
     * Gera os pacotes de confirmação. Implementada por mim, está em acordo com 
     * o 802.15.4.
     * @param buf Usado apenas para verificação do id do pacote
     * @param dAck o pacote ack a ser configurado
     * @return Retorna o pacote ack configurado
     */
    char* generateAck(const char *buf, char* dAck) {
        unsigned char packId;
        packId = (unsigned char) buf[2];

        // ack frame: type 010
        dAck[0] = 0x02;
        dAck[1] = 0x00;

        // seq nr
        dAck[2] = packId;

        uint16_t crc = crc16(dAck, 3);

        dAck[3] = crc & 0xFF;
        dAck[4] = crc >> 8;
        dAck[5] = 0x7f;

        return dAck;
    }

    /**
     * Gera os pacotes de dados.
     * Essa função é da implementação original, melhorei ela um pouco, 
     * mas precisa ser muito melhorada ainda. Os autores dizem que o pacote 
     * está em acordo com o padrão 802.15.4. Confiei neles, conferi 
     * tudo exceto o subfild de controle.
     */
    void generate_mac(const char *buf, int len, char* addr_dest) {

        char payload[1];
        payload[0] = 'D';

        // FCF
        // data frame, no security
        d_msg[0] = 0x61;
        d_msg[1] = 0x88;

        // seq nr
        d_msg[2] = d_seq_nr++;

        // addr info
        d_msg[3] = 0xcd;
        d_msg[4] = 0xab;
        d_msg[5] = addr_dest[0];
        d_msg[6] = addr_dest[1];
        d_msg[7] = mac_addr_1;
        d_msg[8] = mac_addr_2;
        d_msg[9] = 'D';

        std::memcpy(d_msg + 10, buf, len);

        uint16_t crc = crc16(d_msg, len + 10);

        d_msg[10 + len] = crc & 0xFF;
        d_msg[11 + len] = crc >> 8;
        d_msg[12 + len] = 0x7f;

        d_msg_len = 10 + len + 3;
    }

    void print_message() {
        for (int i = 0; i < d_msg_len; i++) {
            dout << std::setfill('0') << std::setw(2) << std::hex << ((unsigned int) d_msg[i] & 0xFF) << std::dec << " ";
            if (i % 16 == 15) {
                dout << std::endl;
            }
        }
        dout << std::endl;
    }

    int get_num_packet_errors() {
        return d_num_packet_errors;
    }

    int get_num_packets_received() {
        return d_num_packets_received;
    }

    float get_packet_error_ratio() {
        return float(d_num_packet_errors) / d_num_packets_received;
    }

private:
    bool d_debug;
    bool is_coordinator;
    int d_msg_offset;
    int d_msg_len;
    int control_pack_len;
    int indexDestNode;
    int indexLocalMac;


    uint8_t d_seq_nr;
    char d_msg[256];

    int d_num_packet_errors;
    int d_num_packets_received;

    uint16_t d_rnp_rtx;
    uint16_t d_rnp_nr_pkts;
    uint16_t d_confirmed_pkts;
    float d_snr; 
    decltype(std::chrono::high_resolution_clock::now()) d_start_time;
    decltype(std::chrono::high_resolution_clock::now()) d_end_time;
};

tdma::sptr
tdma::make(int mac_addr, int dest_node, bool debug, bool is_coord) {
    return gnuradio::get_initial_sptr(new tdma_impl(mac_addr, dest_node, debug, is_coord));
}

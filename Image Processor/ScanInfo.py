# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 15:20:55 2020

@author: yaoji
"""

import sys
sys.path.append("../ui/")
sys.path.append("../Model/")
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import pyqtSignal
from ScanInfo_ui import Ui_ScanInfo
import conversion as cnv

class myScanInfo(QWidget, Ui_ScanInfo):
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def init_UI(self):
        pass
    
    def init_scanInfo(self, data):
        # Title
        file_name = data.path[-12:]
        self.setWindowTitle('Scan Data Info --- ' + str(file_name))

        # Date and Time
        self.label_date.setText(str(data.time)[0:10])
        self.label_time.setText(str(data.time)[11:19])

        # Delay
        self.label_move_delay.setText(str(data.move_delay))
        self.label_read_delay.setText(str(data.measure_delay))
        self.label_line_delay.setText(str(data.line_delay))

        # Scan direction
        direction = ', Read Forward' if data.dir_x else ', Read Backward'
        order = 'Y first' if data.channel_x == 0x1f else 'X first'
        self.label_scan_direction.setText(order + direction)
        # Scan protection
        scan_protection_dict = {0: 'No protection', 1: 'Stop scan', 2: 'Auto 0 and continue', 3: 'Auto to previous midpoint and continue'}
        if data.scan_protect_flag == 0:
            self.label_scan_protection.setText(scan_protection_dict[data.scan_protect_flag])
        else:
            limit = round(cnv.bv(data.limit + cnv.vb(0.0, 'a'), 'a'), 5)  # Limit for scan protection
            self.label_scan_protection.setText(scan_protection_dict[data.scan_protect_flag] + 'with Zout limit ' + str(limit) + 'V')
        # Tip protection
        tip_protection = 'Protected' if data.tip_protection else 'No protection'
        tip_protect_data = ', retracted Offset fine '
        if data.tip_protection:
            self.label_tip_protection.setText(tip_protection + tip_protect_data + str(data.tip_protect_data) + ' bits')
        else:
            self.label_tip_protection.setText(tip_protection)
        # Current protection
        current_protection = 'Protected' if data.current_protection else 'No protection'
        current_protect_data = ', stop when I > '
        if data.current_protection:
            self.label_current_protection.setText(current_protection + current_protect_data + str(round(data.ilimit,1)) + 'nA')
        else:
            self.label_current_protection.setText('')

        # !!! Feedback off pre-scan
        self.label_pre_scan.setText('')
        self.label_advance_z.setText(str(data.advance_bit))

        # Status
        bias_dac = '20bit DAC' if data.bias_dac else '16bit DAC'
        self.label_bias_dac.setText(bias_dac)
        bias = cnv.bv(data.lastdac[13],'d',data.dacrange[13])
        self.label_bias.setText(str(bias))
        bias_dither = 'ON' if data.lastdigital[0] == 1 else 'OFF'
        self.label_bias_dither.setText(str(bias_dither))
        z_dither = 'ON' if data.lastdigital[1] == 1 else 'OFF'
        self.label_zdither.setText(str(z_dither))
        feedback = 'ON' if data.lastdigital[2] == 1 else 'OFF'
        self.label_feedback.setText(str(feedback))
        x_in = data.lastdac[0] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_xin.setText(str(x_in))
        x_offset = data.lastdac[1] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_xoffset.setText(str(x_offset))
        z_offset_fine = data.lastdac[2] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_zoffset_fine.setText(str(z_offset_fine))
        z_offset = data.lastdac[3] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_zoffset.setText(str(z_offset))
        i_set = cnv.b2i(data.lastdac[5], data.preamp_gain, data.dacrange[5])
        self.label_iset.setText(str(i_set))
        y_offset = data.lastdac[14] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_yoffset.setText(str(y_offset))
        y_in = data.lastdac[15] - 0x8000 if not data.bias_dac else data.lastdac[0] - 0x80000
        self.label_yin.setText(str(y_in))
        x_gain = '10.0' if data.lastgain[0] == 0 else ('1.0' if data.lastgain[0] == 1 else '0.1')
        self.label_xgain.setText(x_gain)
        y_gain = '10.0' if data.lastgain[1] == 0 else ('1.0' if data.lastgain[1] == 1 else '0.1')
        self.label_ygain.setText(y_gain)
        z1_gain = '10.0' if data.lastgain[2] == 0 else ('1.0' if data.lastgain[2] == 1 else '0.1')
        self.label_zgain1.setText(z1_gain)
        z2_gain = '10.0' if data.lastgain[3] == 3 else ('1.0' if data.lastgain[3] == 1 else '0.1')
        self.label_zgain2.setText(z2_gain)
        preamp_gain = data.preamp_gain
        self.label_preamp_gain.setText(str(preamp_gain))
        dac_range_dict = {0:'0 to 5V', 1: '0 to 10V', 2: '0 to 20V', 4: '0 to 40V', 9: '-V to +5V', 10: '-10V to +10V', 12: '-20V to +20V', 14: '-2.5V to +2.5V'}
        bias_range = dac_range_dict[data.dacrange[13]]
        self.label_bias_range.setText(bias_range)

        # !!! Lock-in parameter
        if data.lockin_flag:
            self.label_modulation_type.setText(data.osc_type)
            self.label_osc_amp.setText(str(data.osc_rms))
            self.label_lockin_frequency.setText(str(data.lockin_freq))
            self.label_sensitivity1.setText(str(data.sen1))
            self.label_sensitivity2.setText(str(data.sen2))
            self.label_osc_frequency.setText(str(data.osc_freq))
            self.label_phase1.setText(str(data.phase1))
            self.label_phase2.setText(str(data.phase2))
            self.label_offset1.setText(str(data.offset1))
            self.label_offset2.setText(str(data.offset2))
            self.label_time_const1.setText(str(data.tc1))
            self.label_time_const2.setText(str(data.tc2))
        else:
            self.label_modulation_type.setText('NA')
            self.label_osc_amp.setText('NA')
            self.label_lockin_frequency.setText('NA')
            self.label_sensitivity1.setText('NA')
            self.label_sensitivity2.setText('NA')
            self.label_osc_frequency.setText('NA')
            self.label_phase1.setText('NA')
            self.label_phase2.setText('NA')
            self.label_offset1.setText('NA')
            self.label_offset2.setText('NA')
            self.label_time_const1.setText('NA')
            self.label_time_const2.setText('NA')

        # Sequence
        self.label_seq_name.setText(data.seq.name)
        seq_feedback = 'ON' if data.seq.feedback else 'OFF'
        self.label_seq_feedback.setText(seq_feedback)
        seq_bias_dither = 'ON' if data.seq.ditherB else 'OFF'
        self.label_seq_bias_dither.setText(seq_bias_dither)
        seq_z_dither = 'ON' if data.seq.ditherZ else 'OFF'
        self.label_seq_z_dither.setText(seq_z_dither)

        # If command_list and command do not match, use command_list, else command
        if len(data.seq.command_list) != len(data.seq.command):

            # Init 5 sequence lists
            data.seq.command = []
            data.seq.channel = []
            data.seq.option1 = []
            data.seq.option2 = []
            data.seq.data = []

            # Translate command_list and data_list to 5 sequence lists
            for i in range(data.seq.seq_num):
                if data.seq.command_list[i] == 0x00:
                    data.seq.command += ['Wait']
                    channel = data.seq.command_list[i] - 0x00
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i])]
                    data.seq.option1 += [0]
                    data.seq.option2 += [0]
                elif (data.seq.command_list[i] >= 0x40) and (data.seq.command_list[i] <= 0x45):
                    data.seq.command += ['Dout']
                    channel = data.seq.command_list[i] - 0x40
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0x1)]
                    data.seq.option1 += [0]
                    data.seq.option2 += [0]
                elif (data.seq.command_list[i] >= 0xc0) and (data.seq.command_list[i] <= 0xdc):
                    data.seq.command += ['Read']
                    channel = (data.seq.command_list[i] - 0xc0) / 4
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0xffff)]
                    data.seq.option1 += [0]
                    data.seq.option2 += [0]
                elif data.seq.command_list[i] == 0x20:
                    data.seq.command += ['Match']
                    data.seq.channel += ['NA']
                    data.seq.data += [str(data.seq.data_list[i] & 0xffff)]
                    data.seq.option1 += [data.seq.data_list[i] & 0x80000000]
                    data.seq.option2 += [0]
                elif (data.seq.command_list[i] >= 0x60) and (data.seq.command_list[i] <= 0x70):
                    data.seq.command += ['Shift']
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0xfffff)]
                    data.seq.option1 += [(data.seq.data_list[i] & 0x80000000) >> 31]
                    data.seq.option2 += [0]
                elif (data.seq.command_list[i] >= 0x80) and (data.seq.command_list[i] <= 0x90):
                    data.seq.command += ['Aout']
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0xfffff)]
                    data.seq.option1 += [0]
                    data.seq.option2 += [0]
                elif (data.seq.command_list[i] >= 0x80) and (data.seq.command_list[i] <= 0x90):
                    data.seq.command += ['Ramp']
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0xfffff)]
                    data.seq.option1 += [0]
                    data.seq.option2 += [(data.seq.data_list[i] & 0xfff00000) >> 20]
                elif (data.seq.command_list[i] >= 0x80) and (data.seq.command_list[i] <= 0x90):
                    data.seq.command += ['ShiftRamp']
                    data.seq.channel += [
                        list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
                    data.seq.data += [str(data.seq.data_list[i] & 0xfffff)]
                    data.seq.option1 += [(data.seq.data_list[i] & 0x80000000) >> 31]
                    data.seq.option2 += [(data.seq.data_list[i] & 0x7ff00000) >> 20]

        # Use 5 sequence lists to generate str description list
        seq_description = []    # Init str description list
        self.listWidget_seq.clear()    # Init list widget
        for i in range(data.seq.seq_num):
            if data.seq.command[i] == 'Wait':
                seq_description += [str(i+1) + '  Wait ' + data.seq.data[i] + ' us']
            elif data.seq.command[i] == 'Match':
                option = '  Fast' if data.seq.option1[i] else '  Slow'
                seq_description += [str(i+1) + option + ' Match current']
            elif data.seq.command[i] == 'Dout':
                status = 'ON' if data.seq.data[i] else 'OFF'
                if data.seq.channel[i] == 'DitherZ':
                    seq_description += [str(i+1) + '  Z dither ' + status]
                elif data.seq.channel[i] == 'DitherB':
                    seq_description += [str(i+1) + '  Bias dither ' + status]
                elif data.seq.channel[i] == 'Feedback':
                    seq_description += [str(i+1) + '  Feedback ' + status]
            elif data.seq.command[i] == 'Shift':
                direction = ' Up' if data.seq.option1[i] else ' Down'
                if (data.seq.channel[i] == 'Z offset fine') or (data.seq.channel[i] == 'Z offset'):
                    seq_description += [str(i+1) + '  Shift ' + data.seq.channel[i] + direction + ' by ' + data.seq.data[i] + ' bits']
                elif data.seq.channel[i] == 'Iset':
                    seq_description += [str(i+1) + '  Shift ' + data.seq.channel[i] + direction + ' by ' + data.seq.data[i] + ' nA']
                else:
                    seq_description += [str(i+1) + '  Shift ' + data.seq.channel[i] + direction + ' by ' + data.seq.data[i] + ' volts']
            elif data.seq.command[i] == 'Aout':
                if data.seq.option1 == 1:
                    seq_description += [str(i+1) + '  Analog Output ' + data.seq.channel[i] + ' to Original']
                else:
                    if (data.seq.channel[i] == 'Z offset fine') or (data.seq.channel[i] == 'Z offset'):
                        seq_description += [str(i+1) + '  Analog Output ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' bits']
                    elif data.seq.channel[i] == 'Iset':
                        seq_description += [str(i+1) + '  Analog Output ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' nA']
                    else:
                        seq_description += [str(i+1) + '  Analog Output ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' volts']
            elif data.seq.command[i] == 'Ramp':
                if data.seq.option1[i] == 1:
                    seq_description += [str(i+1) + '  Ramp ' + data.seq.channel[i] + ' to Original with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
                else:
                    if (data.seq.channel[i] == 'Z offset fine') or (data.seq.channel[i] == 'Z offset'):
                        seq_description += [str(i+1) + '  Ramp ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' bits with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
                    elif data.seq.channel[i] == 'Iset':
                        seq_description += [str(i+1) + '  Ramp ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' nA with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
                    else:
                        seq_description += [str(i+1) + '  Ramp ' + data.seq.channel[i] + ' to ' + data.seq.data[i] + ' volts with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
            elif data.seq.command[i] == 'Read':
                seq_description += [str(i+1) + '  Read ' + data.seq.channel[i] + ' ' + data.seq.data[i] + ' times']
            elif data.seq.command[i] == 'ShiftRamp':
                if (data.seq.channel[i] == 'Z offset fine') or (data.seq.channel[i] == 'Z offset'):
                    seq_description += [str(i+1) + '  ShiftRamp ' + data.seq.channel[i] + ' by ' + data.seq.data[i] + ' bits with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
                elif data.seq.channel[i] == 'Iset':
                    seq_description += [str(i+1) + '  ShiftRamp ' + data.seq.channel[i] + ' by ' + data.seq.data[i] + ' nA with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']
                else:
                    seq_description += [str(i+1) + '  ShiftRamp ' + data.seq.channel[i] + ' by ' + data.seq.data[i] + ' volts with speed ' + str(float(data.seq.option2[i])/10.0) + ' bits/ms']

            self.listWidget_seq.addItem(seq_description[i])

        # Other information
        self.label_of_image.setText(str(data.data.shape[0]))
        self.label_steps.setText(str(data.step_num))
        self.label_step_size.setText(str(data.step_size))
        match_curr = 'ON' if data.match_curr else 'OFF'
        self.label_match_curr.setText(match_curr)
    
    # Emit close signal
    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myScanInfo()
    window.show()
    sys.exit(app.exec_())

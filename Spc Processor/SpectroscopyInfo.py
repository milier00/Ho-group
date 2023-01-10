# -*- coding: utf-8 -*-
"""
@Date     : 2020/12/24 17:35:45
@Author   : milier00
@FileName : BetweenPasses.py
"""
import sys
sys.path.append("./ui/")
sys.path.append("./model/")
from PyQt5.QtWidgets import QApplication, QWidget, QSpinBox
from PyQt5.QtCore import pyqtSignal
from SpectroscopyInfo_ui import Ui_SpectroscopyInfo
import conversion as cnv

class mySpectroscopyInfo(QWidget, Ui_SpectroscopyInfo):
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.idling = True
        self.setupUi(self)
        self.init_UI()

    def init_UI(self):
        pass

    def init_spcInfo(self, data):
        # Title
        file_name = data.path
        self.setWindowTitle('Spectroscopy Data Info --- ' + str(file_name))

        # Date and Time
        self.label_date.setText(str(data.time)[0:10])
        self.label_time.setText(str(data.time)[11:19])

        # Options
        start = round(cnv.bv(data.start, 'd', data.dacrange[13]) * 1000, 1)
        self.label_min.setText(str(start)+' mV')
        bias_mid = 0x80000 if data.bias_dac else 0x8000
        step = round(cnv.bv(data.step+bias_mid, 'd', data.dacrange[13]) * 1000, 3)
        self.label_step.setText(str(step)+' mV')
        self.label_of_data_pts.setText(str(data.data_num))
        self.label_move_delay.setText(str(data.move_delay))
        self.label_delta.setText(str(data.delta_data))
        channel_dict = {13: 'Bias', 2: 'Z fine'}
        self.label_ramp_ch.setText(channel_dict[data.ramp_ch-16])
        scan_direction_dict = {0:'Read forward only', 1:'Read backward only', 2:'Read both forward and backward but do not average', 3:'Average both forward and backward'}
        scan_direction = scan_direction_dict[data.scan_dir]
        self.label_scan_direction.setText(scan_direction)
        self.label_of_passes.setText(str(data.pass_num))
        self.label_read_delay.setText(str(data.read_delay))

        # Status
        bias_dac = '20bit DAC' if data.bias_dac else '16bit DAC'
        self.label_bias_dac.setText(bias_dac)
        bias = cnv.bv(data.lastdac[13], 'd', data.dacrange[13])
        self.label_bias.setText(str(bias))
        bias_dither = 'ON' if data.lastdigital[0] == 1 else 'OFF'
        self.label_bias_dither_2.setText(bias_dither)
        z_dither = 'ON' if data.lastdigital[1] == 1 else 'OFF'
        self.label_z_dither.setText(z_dither)
        feedback = 'ON' if data.lastdigital[2] == 1 else 'OFF'
        self.label_feedback.setText(feedback)
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
        dac_range_dict = {0: '0 to 5V', 1: '0 to 10V', 2: '0 to 20V', 4: '0 to 40V', 9: '-V to +5V', 10: '-10V to +10V',
                          12: '-20V to +20V', 14: '-2.5V to +2.5V'}
        bias_range = dac_range_dict[data.dacrange[13]]
        self.label_bias_range.setText(str(bias_range))

        # !!! Lock in parameter
        if data.lockin_flag:
            self.label_osc_amp.setText(str(data.osc_rms))
            self.label_lockin_freq.setText(str(data.lockin_freq))
            self.label_sen1.setText(str(data.sen1))
            self.label_sen2.setText(str(data.sen2))
            self.label_osc_freq.setText(str(data.osc_freq))
            self.label_offset1.setText(str(data.offset1))
            self.label_offset2.setText(str(data.offset2))
            self.label_modulation_type.setText(data.osc_type)
            self.label_phase1.setText(str(data.phase1))
            self.label_phase2.setText(str(data.phase2))
            self.label_tc1.setText(str(data.tc1))
            self.label_tc2.setText(str(data.tc2))
        else:
            self.label_osc_amp.setText('NA')
            self.label_lockin_freq.setText('NA')
            self.label_sen1.setText('NA')
            self.label_sen2.setText('NA')
            self.label_osc_freq.setText('NA')
            self.label_offset1.setText('NA')
            self.label_offset2.setText('NA')
            self.label_modulation_type.setText('NA')
            self.label_phase1.setText('NA')
            self.label_phase2.setText('NA')
            self.label_tc1.setText('NA')
            self.label_tc2.setText('NA')

        # Correction
        self.label_every.setText(str(data.corr_pass_num))
        z_correction = 'ON' if data.z_flag else 'OFF'
        self.label_z_correction.setText(z_correction)
        match_curr = 'ON' if data.match_flag else 'OFF'
        self.label_match_curr.setText(match_curr)
        track = 'ON' if data.track_flag else 'OFF'
        self.label_track.setText(track)
        self.label_feedback_on_del.setText(str(data.feedback_delay)+' ms')
        self.label_pre_scan.setText(str(data.pre_scan))
        self.label_re_scan.setText(str(data.rescan))
        pattern_center_x = data.pattern[0]
        self.label_pattern_center_x.setText(str(pattern_center_x))
        pattern_center_y = data.pattern[1]
        self.label_pattern_center_y.setText(str(pattern_center_y))
        pattern_size = data.pattern[2]
        self.label_pattern_size.setText(str(pattern_size))

        # Sequence
        self.label_seq_name.setText(str(data.seq.name))
        feedback_seq = 'ON' if data.seq.feedback else 'OFF'
        self.label_seq_feedback.setText(feedback_seq)
        bias_dither_seq = 'ON' if data.seq.ditherB else 'OFF'
        self.label_bias_dither.setText(bias_dither_seq)
        z_dither_seq = 'ON' if data.seq.ditherZ else 'OFF'
        self.label_zdither.setText(z_dither_seq)

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
        self.listWidget_seq.clear()  # Init list widget
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
                    if (data.seq.channel[i] == 'Z offset fine') or (data.seq.channel[i] =='Z offset'):
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

        # Points
        points = []
        for point in data.point_list:
            x = point[0] - 32768
            y = point[1] - 32768
            points += [(x, y)]
        self.tableWidget_pts.setRowCount(len(points))
        for i in range(len(points)):
            x = QSpinBox()
            x.setMinimum(-32768)
            x.setMaximum(32767)
            x.setValue(points[i][0])
            x.setReadOnly(True)
            y = QSpinBox()
            y.setMinimum(-32768)
            y.setMaximum(32767)
            y.setValue(points[i][1])
            y.setReadOnly(True)
            self.tableWidget_pts.setCellWidget(i, 0, x)
            self.tableWidget_pts.setCellWidget(i, 1, y)

    # Emit close signal
    def closeEvent(self, event):
        if self.idling:
            self.close_signal.emit()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mySpectroscopyInfo()
    window.show()
    sys.exit(app.exec_())
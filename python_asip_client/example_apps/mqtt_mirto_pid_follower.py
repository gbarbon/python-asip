from mirto_robot_classes.mqtt_mirto_robot import MQTTMirtoRobot
import getopt
import math
import sys
import time

class MQTTMirtoPIDFollower(MQTTMirtoRobot):

    def __init__(self, Broker, BoardID):

        sys.stdout.write("Setting up in 2 seconds...\n")
        time.sleep(2)
        sys.stdout.write("Starting now\n")
        MQTTMirtoRobot.__init__(self,Broker, BoardID)

        self.howTo = "AsipMirtoPIDFollower usage:\n"\
                + "You can invoke AsipMirtoPIDFollower with default parameter without providing \n"\
                + "arguments on the command line. Otherwise, you need to provide exactly 7 arguments:\n"\
                + " 1. power: this is an integer number between 0 and 100. Default 75\n"\
                + " 2. maxDelta: this is an integer providing the maximum correction value (0-100), default 75\n"\
                + " 3. Proportional correction constant: this is a double, default 0.05\n"\
                + " 4. Derivative correction constant: this is a double, default 1.6\n"\
                + " 5. Integral correction constant: this is a double, default 0.0001\n"\
                + " 6. Frequence of updates: this is an integer, default 30 (ms)\n"\
                + " 7. Cut-off IR value: this is the value under which we define black. Default 40.\n"

        self.cutOffIR = 40
        self.PWR = 50
        self.freq = 35 # frequency of updates;
        self.maxDelta = self.PWR # max correction

        self.Kp = 0.050
        self.Kd = 1.6
        self.Ki = 0.0001

        self.curError = 2000
        self.prevError = 2000

        sys.stdout.write("Robot set up completed\n")
        time.sleep(0.5)

    # ************ BEGIN PUBLIC METHODS *************

    def get_how_to(self):
        return self.howTo

    def set_how_to(self, string):
        self.howTo = string

    def get_cut_off_ir(self):
        return self.cutOffIR

    def set_cut_off_ir(self, cutOffIR):
        self.cutOffIR = cutOffIR

    def get_pwr(self):
        return self.PWR

    def set_pwr(self, pWR):
        self.PWR = pWR

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_max_delta(self):
        return self.maxDelta

    def set_max_delta(self, maxDelta):
        self.maxDelta = maxDelta

    def get_kp(self):
        return self.Kp

    def set_kp(self, kp):
        self.Kp = kp

    def get_kd(self):
        return self.Kd

    def set_kd(self, kd):
        self.Kd = kd

    def get_ki(self):
        return self.Ki

    def set_ki(self, ki):
        self.Ki = ki

    # ************ END PUBLIC METHODS *************


    # ************ BEGIN PRIVATE METHODS *************

    def cut_ir(self, i_n):
        if i_n < self.cutOffIR:
            return 0
        else:
            return i_n

    def compute_error(self, left, middle, right, previous):
        if (left+right+middle) == 0:
            return previous
        else:
            return (middle*2000 + right*4000) / (left + middle + right)

    def navigate(self):
        try:
            time_now = int(round(time.time() * 1000))
            old_time = 0

            proportional = 0
            integral = 0
            derivative = 0
            correction = 0

            # print IR values every interval milliseconds
            while True:
                time_now = int(round(time.time() * 1000))

                if (time_now - old_time) > self.freq:

                    left_ir = self.cut_ir(self.get_ir(2))
                    middle_ir = self.cut_ir(self.get_ir(1))
                    right_ir = self.cut_ir(self.get_ir(0))

                    if (left_ir==0) and (middle_ir==0) and (right_ir==0):
                        # This means that we lost the track. We keep doing what we
                        # were doing before.
                        self.curError = self.prevError
                    else:
                        self.curError = self.compute_error(left_ir,middle_ir,right_ir,self.prevError)

                    proportional = self.curError - 2000

                    if proportional == 0:
                        integral = 0;
                    else:
                        integral += proportional

                    derivative = proportional - (self.prevError - 2000)
                    self.prevError = self.curError
                    correction = int( math.floor(self.Kp*proportional + self.Ki*integral + self.Kd*derivative))
                    delta = correction

                    if delta>self.maxDelta:
                        delta=self.maxDelta
                    elif delta < (-self.maxDelta):
                        delta = (-self.maxDelta)

                    sys.stdout.write("IR: {} {} {}\n".format(left_ir, middle_ir, right_ir))
                    sys.stdout.write("Delta: {}\n".format(delta))

                    if delta < 0:
                        self.set_motors( int(2.55*(self.PWR+delta)), int(2.55*(-self.PWR)))
                    else:
                        self.set_motors( (int) (2.55*self.PWR), (int) (-(self.PWR-delta)*2.55) )

                    old_time = time_now
                # We do not want to flood the serial port if setting motors is enabled
                time.sleep(0.01)
        except Exception as e:
            self.stop_motors()
            sys.stdout.write("Exception caught in navigate {}\n".format(e))

    def main(self, argv=None):

        # try:
        #     opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
        # except getopt.GetoptError:
        #     sys.stdout.write("mqtt_mirto_pid_follower.py ...\n")
        #     sys.exit(2)

        if argv == None : # in python first argument is always filename
            # No command line parameters provided
            self.set_pwr(50)
            self.set_max_delta(50)

            self.set_kp(0.015)
            self.set_kd(0)
            self.set_ki(0)

            self.set_freq(50)
            self.set_cut_off_ir(50)

            self.navigate()

        # TODO: argument not working now, improvement needed
        elif len(argv)== 8:
            # the order is: power, maxDelta, Kp, Kd, Ki, freq, cutoffIR
            try:
                self.set_pwr(argv[1])
                self.set_max_delta(argv[2])

                self.set_kp(argv[3])
                self.set_kd(argv[4])
                self.set_ki(argv[5])

                self.set_freq(argv[6])
                self.set_cut_off_ir(argv[7])
            except Exception as e:
                sys.stdout.write("Error parsing command line parameters! The correct syntax is: ");
                sys.stdout.write(self.get_how_to())
                sys.stdout.write("Exception caught is: {}\n".format(e))

            self.navigate()

        else:
            sys.stdout.write("Error parsing command line parameters! The correct syntax is: ")
            sys.stdout.write(self.get_how_to())

if __name__ == "__main__":
    Broker = "192.168.0.103"
    BoardID = "test" # "test" is the name of the board in the python bridge, while "board4" is the name in the java one
    MQTTMirtoPIDFollower(Broker, BoardID).main()
    #MQTTMirtoPIDFollower(Broker, BoardID).main(sys.argv[1:])
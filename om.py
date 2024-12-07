import random
import numpy as np
import math
import time
import os

class OM():
    def __init__(self, vehicle_num, time_lim, time_left):
        self.vehicles_position = np.zeros((vehicle_num,2),dtype=np.int32)
        self.vehicles_speed = np.zeros(vehicle_num,dtype=np.int32)
        self.speed_range = [10, 15, 30]
        self.vehicle_num = vehicle_num
        self.time_lim = time_lim
        self.time_left = time_left
        self.seed = np.zeros(vehicle_num)
        self.vehicles_lefttime = np.ones(vehicle_num,dtype=np.float32) * self.time_left
        self.generator()
        
    def reset(self):
        self.vehicles_position = np.zeros(self.vehicles_position.shape[0],dtype=np.int32)
        self.vehicles_lefttime = np.ones(self.vehicles_position.shape[0],dtype=np.float32) * self.time_lim
        self.time_left = self.time_lim
    
    def generator(self):
        for i in range(self.vehicle_num):
            self.seed[i] = np.random.rand()
            self.vehicles_speed[i] = random.choice(self.speed_range)
    
    def scaling(self, seed):
        stoch = 1 - np.exp(seed-1)
        return stoch
    
    def assignment(self, task_appear_rate, target):
        sucess = False
        reward = target[2]
        max_reward = 0
        opt_UAV = -1
        task_time = np.arange(5,31)
        # print("attemp start: ")
        while True:
            available_vehicle = np.where(self.vehicles_lefttime >= self.time_left)[0]
            if len(available_vehicle) == 0:
                self.time_left -= 1
                for i in available_vehicle:
                    self.vehicles_lefttime[i] -= 1
                continue
            # print(available_vehicle)
            for i in available_vehicle:
                distance = np.linalg.norm(self.vehicles_position[i]-target[:2])
                expected_time = task_time + distance/self.vehicles_speed[i]
                prob_exceed_time = (expected_time<self.time_left).sum()/26
                expected_reward = prob_exceed_time*task_appear_rate*reward*self.scaling(self.seed[i])
                if expected_reward > max_reward:
                    max_reward = expected_reward
                    opt_UAV = i
            sucess_check = random.random()
            if sucess_check > 0.5:
                sucess = True
                break
            elif self.time_left <= 0:
                break
            self.time_left -= 1
            for i in available_vehicle:
                self.vehicles_lefttime[i] -= 1
        
        if sucess:
            distance = np.linalg.norm(self.vehicles_position[opt_UAV]-target[:2])
            time_comsumption = distance/self.vehicles_speed[opt_UAV] + target[3]
            self.vehicles_lefttime[opt_UAV] -= time_comsumption
            # print[opt_UAV]
            # print("time left", self.time_left)
            # print("time consumption", time_comsumption)
            # print("opt UAV left time: ", self.vehicles_lefttime[opt_UAV])
            if self.vehicles_lefttime[opt_UAV] < 0:
                # print("Exceed")
                self.vehicles_lefttime[opt_UAV] += time_comsumption
                return 0, -1, self.time_left
            else:
                self.vehicles_position[opt_UAV] = target[:2]
                return reward, opt_UAV, self.time_left
        else:
            return 0, -1, self.time_left
    

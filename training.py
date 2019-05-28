from patient import ColdTime
from qlearning import q_learning_model
from environment import Environment
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import csv

def update(days,values):
    s_ = np.zeros((1, 4), int)
    for episode in range(0,episode_number):
        delaytime = 0
        while True:
            Reward = 0
            getout1=False
            getout2 = False
            timeofill = 0
            energy_change = 0
            energy_sum = 0
            for n in range(0, 15):
                s[n] = [n//5-1, n % 5, 5, 0]
            for days_number in range(days):
                for n in range(0,24):
                    p_actions=[]
                    new_p = []
                    s_[0] = [0,-1,0,0]
                    s_[0][0]=increas[days_number][n]
                    s_[0][1]=max[days_number][n]

                    now=(s_[0][0]+1)*5+s_[0][1]
                    energy_sum = energy_sum + s[now][2]/(s[now][2]+s[now][3])

                    while True:
                        if s[now][2]==10:
                            p_actions.extend([1,3])
                        if s[now][3]==10:
                            p_actions.extend([2, 3])
                        if s[now][2] == 1:
                            p_actions.extend([0, 2])
                        if s[now][3] == 0:
                            p_actions.extend([0, 1])
                        for i in p_actions:
                            if i not in new_p:
                                new_p.append(i)
                        action = RL['obj'+str(e)].choose_action(str(s[now]),new_p,episode,values)
                        s_[0][2],s_[0][3]= env.change(s[now][2],s[now][3],action) # 执行这个动作得到反馈（下一个状态s 奖励r ）
                        break
                    illpoint = 0
                    if n==23:
                        s_[0][0] = increas[days_number+1][0]
                        s_[0][1] = max[days_number+1][0]
                    else:
                        s_[0][0] = increas[days_number][n + 1]
                        s_[0][1] = max[days_number][n+1]

                    if s_[0][1] == 4:
                        for second in range((days_number * 24 + n+1) * 3600, (days_number * 24 + n + 2) * 3600):
                            if illtime[0][second] >= 140:
                                illpoint = second
                                break
                        timeofill+=1

                    if days_number == days - 1 and n == 22:
                        next = (s_[0][0] + 1) * 5 + s_[0][1]
                        energy_sum = energy_sum+s[next][2]/(s[next][2]+s[next][3])
                        energy_change =100*(energy_sum-days*24)/days/24

                    if n == 23:
                        r,d = env.reward(days_number+1,0, s_[0][1], s_[0][2], s_[0][3],energy_change,illpoint)
                    else:
                        r,d = env.reward(days_number,n+1, s_[0][1], s_[0][2], s_[0][3], energy_change,illpoint)
                    RL['obj' + str(e)].rl(str(s[now]), action, r, str(s_[0])) # 更新状态
                    Reward=Reward+r
                    if d > 4:
                        delaytime += 1
                        print("bullshit!**",delaytime)
                        getout1=True
                        break
                    next = (s_[0][0]+1) * 5 + s_[0][1]
                    s[next][2] = s_[0][2]
                    s[next][3] = s_[0][3]
                    if days_number == days - 1 and n == 22:
                        break
                if getout1==True:
                    getout2=True
                    break
            if getout2==True:
                continue
            else:
                y[e][episode] =Reward
            break
        print(episode,",",y[e][episode])

def mk(inputdata):
#输入numpy数组
    n=inputdata.shape[0]
    var=n*(n-1)*(2*n+5)/18
    sv=np.sqrt(var)
    #sv为标准差
    s=0
    z=0
    for i in np.arange(n):
        if i <=(n - 1):
            for j in np.arange(i+1,n):
                if inputdata[j]> inputdata[i]:
                    s=s+1
                elif inputdata[j]< inputdata[i]:
                    s=s-1
                else:
                    s=s
    if s > 0:
        z= (s - 1) / sv
    elif s < 0:
        z= (s+ 1) / sv
    return z

if __name__ == "__main__":
    days=1
    episode_number=1000
    inter=25
    e_number=3
    coti = ColdTime(days)
    getilltime=coti.getilltime()
    env=Environment()
    illtime=np.zeros((1,days*24*3600))
    x=np.zeros(episode_number//inter)
    for i in range(episode_number//inter):
        x[i]=(i*1)*inter
    y = np.zeros((e_number,episode_number))
    for n in range(days):
        for m in range(24*3600):
            illtime[0][n*24*3600+m]= getilltime[n][m]
    s = np.zeros((15, 4),int)

    max = np.zeros((days, 24), int)
    increas = np.zeros((days, 24), int)
    bp = np.zeros(240)
    Rewardmax = 0
    for days_number in range(days):
        for n in range(0, 24):
            for second in range((days_number * 24 + n) * 3600, (days_number * 24 + n + 1) * 3600):
                if illtime[0][second] > max[days_number][n]:
                    max[days_number][n] = illtime[0][second]
            if max[days_number][n] < 90:
                max[days_number][n] = 0
            else:
                if 90 <= max[days_number][n] < 120:
                    max[days_number][n] = 1
                else:
                    if 120 <= max[days_number][n] < 130:
                        max[days_number][n] = 2
                    else:
                        if 130 <= max[days_number][n] < 140:
                            max[days_number][n] = 3
                        else:
                            if 140 <= max[days_number][n] < 180:
                                max[days_number][n] = 4

            for i in range(240):
                bp[i] = illtime[0][(days_number * 24+n) * 3600 + (i +1) * 15-1]
            m = mk(bp)
            if m < -2.32:
                increas[days_number][n] = -1
            else:
                if m > 2.32:
                    increas[days_number][n] = 1
                else:
                    increas[days_number][n] = 0

    RL = {}
    co = ['green', 'red', 'blue']
    for e in range(e_number):
        RL['obj' + str(e)]  = q_learning_model(actions=list(range(env.n_actions)))
        update(days, 0.1*((10)**e))
        for episode in range(0, episode_number):
            if y[e][episode] > Rewardmax:
                Rewardmax = y[e][episode]
    for e in range(e_number):
        y_ = np.zeros(episode_number // inter)
        for episode in range(0, episode_number // inter):
            y_[episode] = math.log(y[e][episode * inter]) / math.log(Rewardmax)
        plt.plot(x, y_, color=co[e], label='value is %s' % (0.1*(10 ** e)))

    plt.xlim(right=episode_number + 1, left=0)
    plt.ylim(top=1.1, bottom=0)
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title('Number of Episode=%s'% episode_number)
    plt.legend()
    plt.savefig('Reward.png')
    plt.show()













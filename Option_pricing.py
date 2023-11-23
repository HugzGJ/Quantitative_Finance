import random
from random import randint

from BM_def import BM
import numpy as np
from Graphics import plot_2d
import matplotlib.pyplot as plt
from Actif_stoch_BS import simu_actif
from Actif_stoch_BS import option_eu_mc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
#from ttkthemes import ThemedTk
from payoffs import payoff_call_eu, payoff_put_eu, payoff_call_asian, payoff_put_asian, close_formulae_call_eu, \
    close_formulae_put_eu, delta_option_eu, gamma_option_eu
from Graphics import display_payoff


class Option_eu:
    #root parameter to
    def __init__(self, type, St, K, t, T, r, sigma, root=None):
        self.type = type
        self.St = St
        self.K = K
        self.t = t
        self.T = T
        self.r = r
        self.sigma = sigma

        if root!= None:
            self.root = root
            self.root.title("European Option Pricing")
            self.root.geometry("400x400")

            self.style = ttk.Style(self.root)
            self.style.theme_use("plastik")

            self.frame = ttk.Frame(root)
            self.frame.pack(pady=20, padx=20)

            self.label = ttk.Label(self.frame, text="European Option Pricing", font=("Helvetica", 16))
            self.label.grid(row=0, column=0, columnspan=2, pady=10)

            self.option_type_label = ttk.Label(self.frame, text="Option Type:")
            self.option_type_label.grid(row=1, column=0, sticky="w")

            self.option_type_var = tk.StringVar()
            self.option_type_combobox = ttk.Combobox(self.frame, textvariable=self.option_type_var, values=["Call EU", "Put EU", "Call Asian", "Put Asian"])
            self.option_type_combobox.grid(row=1, column=1, pady=5)

            self.St_label = ttk.Label(self.frame, text="Current Stock Price:")
            self.St_label.grid(row=2, column=0, sticky="w")

            self.St_entry = ttk.Entry(self.frame)
            self.St_entry.grid(row=2, column=1, pady=5)

            self.K_label = ttk.Label(self.frame, text="Strike Price:")
            self.K_label.grid(row=3, column=0, sticky="w")

            self.K_entry = ttk.Entry(self.frame)
            self.K_entry.grid(row=3, column=1, pady=5)

            self.T_label = ttk.Label(self.frame, text="Time to Maturity (T):")
            self.T_label.grid(row=4, column=0, sticky="w")

            self.T_entry = ttk.Entry(self.frame)
            self.T_entry.grid(row=4, column=1, pady=5)

            self.sigma_label = ttk.Label(self.frame, text="Volatility (sigma):")
            self.sigma_label.grid(row=5, column=0, sticky="w")

            self.sigma_entry = ttk.Entry(self.frame)
            self.sigma_entry.grid(row=5, column=1, pady=5)

            self.calculate_button = ttk.Button(self.frame, text="Calculate Option Price",
                                               command=self.option_price_close_formulae)
            self.calculate_button.grid(row=6, column=0, columnspan=2, pady=10)

            self.result_label = ttk.Label(self.frame, text="", font=("Helvetica", 14))
            self.result_label.grid(row=7, column=0, columnspan=2, pady=10)

    def display_payoff_option(self):
        display_payoff(self.type, self.K)
    def option_price_close_formulae(self):
        if self.type == "Call EU":
            option_price = close_formulae_call_eu(self.St, self.K, self.t, self.T, self.r, self.sigma)
            return option_price
        elif self.type == "Put EU":
            option_price = close_formulae_put_eu(self.St, self.K, self.t, self.T, self.r, self.sigma)
            return option_price
        # elif self.type == "Call Spread":
        #     long_call = close_formulae_call_eu(self.St, self.K, self.t, self.T, self.r, self.sigma)
        #     short_call = close_formulae_call_eu(self.St, self.K_2, self.t, self.T, self.r, self.sigma)
        #     option_price = long_call - short_call
        #     return option_price

    def option_price_mc(self):
        prix_option = 0
        Nmc = 100000
        for i in range(Nmc):
            prix_actif = simu_actif(self.St, self.K, self.t, self.T, self.r, self.sigma)
            if self.type == "Call EU":
                prix_option += payoff_call_eu(prix_actif[-1], self.K)
            elif self.type == "Put EU":
                prix_option += payoff_put_eu(prix_actif[-1], self.K)
            elif self.type == "Call Asian":
                prix_option += payoff_call_asian(prix_actif, self.K)
            elif self.type == "Put Asian":
                prix_option += payoff_put_asian(prix_actif, self.K)
        prix_option = np.exp(-self.r*(self.T-self.t))*prix_option / Nmc

        self.result_label.config(text=f"Option Price: {prix_option:.4f}")
        return prix_option

    # def Delta(self):
    #     option_delta = (delta_option_eu(self.type, self.St, self.K, self.t, self.T, self.r, self.sigma))
    #     return option_delta
    def Delta_DF(self):
        delta_St = 0.00001
        option_delta_St = Option_eu(self.type,self.St+delta_St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.type,self.St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        delta = (option_delta_St - option_option)/delta_St
        return delta
    # def Gamma(self):
    #     option_gamma = (gamma_option_eu(self.type, self.St, self.K, self.t, self.T, self.r, self.sigma))
    #     return option_gamma
    def Gamma_DF(self):
        delta_St = 0.00001
        option_gamma_plus = Option_eu(self.type, self.St + delta_St, self.K, self.t, self.T, self.r,
                                      self.sigma).option_price_close_formulae()
        option_gamma_minus = Option_eu(self.type, self.St - delta_St, self.K, self.t, self.T, self.r,
                                       self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.type,self.St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        gamma = ((option_gamma_plus + option_gamma_minus - 2 * option_option) / delta_St ** 2)
        return gamma
    def Vega_DF(self):
        delta_vol = 0.00001
        option_delta_vol = Option_eu(self.type, self.St, self.K, self.t, self.T, self.r,
                                    self.sigma+delta_vol).option_price_close_formulae()
        option_option = Option_eu(self.type, self.St, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        vega = (option_delta_vol - option_option) / delta_vol
        return vega
    def Theta_DF(self):
        delta_t = 0.00001
        option_delta_t = Option_eu(self.type, self.St, self.K, self.t+delta_t, self.T, self.r,
                                    self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.type, self.St, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        theta = (option_delta_t - option_option) / delta_t
        return theta

class Option_prem_gen(Option_eu):
    def __init__(self, type, St, K, t, T, r, sigma, root=None):
        self.type = type
        self.St = St
        self.K = K
        self.t = t
        self.T = T
        self.r = r
        self.sigma = sigma
        self.options =[]
        self.positions = []
        if type == "Call Spread":
            self.long_call = Option_eu("Call EU", St, K[0], t, T, r, sigma)
            self.short_call = Option_eu("Call EU", St, K[1], t, T, r, sigma)
            self.options = [self.long_call, self.short_call]
            self.positions = [1, -1] #1 : long position, -1 : short position
        if type == "Put Spread":
            self.long_put = Option_eu("Put EU", St, K[0], t, T, r, sigma)
            self.short_put = Option_eu("Put EU", St, K[1], t, T, r, sigma)
            self.options = [self.long_put, self.short_put]
            self.positions = [1, -1]
    '''def option_price_close_formulae(self):
        if self.type == "Call Spread":
            Call1_price = self.long_call.option_price_close_formulae()
            Call2_price = self.short_call.option_price_close_formulae()
            return (Call1_price - Call2_price)'''

    def option_price_close_formulae(self):
        price_basket_options = 0
        for i in range(len(self.options)):
            price_basket_options+=self.positions[i]*self.options[i].option_price_close_formulae()
        return price_basket_options

    def Delta_DF(self):
        delta_St = 0.00001
        option_delta_St = Option_prem_gen(self.type,self.St+delta_St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.type,self.St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        delta = (option_delta_St - option_option)/delta_St
        return delta
    def Gamma_DF(self):
        delta_St = 0.00001
        option_gamma_plus = Option_prem_gen(self.type, self.St + delta_St, self.K, self.t, self.T, self.r,
                                      self.sigma).option_price_close_formulae()
        option_gamma_minus = Option_prem_gen(self.type, self.St - delta_St, self.K, self.t, self.T, self.r,
                                       self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.type,self.St, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        gamma = ((option_gamma_plus + option_gamma_minus - 2 * option_option) / delta_St ** 2)
        return gamma
    def Vega_DF(self):
        delta_vol = 0.00001
        option_delta_vol = Option_prem_gen(self.type, self.St, self.K, self.t, self.T, self.r,
                                    self.sigma+delta_vol).option_price_close_formulae()
        option_option = Option_prem_gen(self.type, self.St, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        vega = (option_delta_vol - option_option) / delta_vol
        return vega
    def Theta_DF(self):
        delta_t = 0.00001
        option_delta_t = Option_prem_gen(self.type, self.St, self.K, self.t+delta_t, self.T, self.r,
                                    self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.type, self.St, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        theta = (option_delta_t - option_option) / delta_t
        return theta
def plot_greek_curves_2d(type_option, greek, K, t_, T, r, vol):
    St_range = range(20, 180, 1)
    Eu_options = ['Call EU', 'Put EU']
    Option_first_gen = ['Call Spread', 'Put Spread']
    if type_option in Eu_options:
        Option = Option_eu
    elif type_option in Option_first_gen:
        Option = Option_prem_gen
    if greek.lower() =='delta':
        Option.greek = Option.Delta_DF
    elif greek.lower() == 'gamma':
        Option.greek = Option.Gamma_DF
    elif greek.lower() == 'vega':
        Option.greek = Option.Vega_DF
    elif greek.lower() == 'theta':
        Option.greek = Option.Theta_DF

    if type(vol) == list:
        moving_param = vol
        moving_param_label = "volatility"
    elif type(T) == list:
        moving_param = T
        moving_param_label = "maturity"
    elif type(r) == list:
        moving_param = r
        moving_param_label = "st rate"
    else:
        greek_list = []
        for i in St_range:
            option_obj = Option(type_option, i, K, t_, T, r, vol)
            greek_list.append(option_obj.greek())
        plot_2d(St_range, greek_list, f"{greek} curve", "Prix de l'actif", greek, True)
        return

    for v in moving_param:
        if moving_param_label == "volatility":
            vol = v
        elif moving_param_label == "maturity":
            T = v
        elif moving_param_label == "st rate":
            r = v
        greek_list = []
        for i in St_range:
            option_obj = Option(type_option, i, K, t_, T, r, vol)
            greek_list.append(option_obj.greek())
        plot_2d(St_range, greek_list, f"{greek} curve - {type_option}", "Prix de l'actif", greek, False)
    moving_param = [moving_param_label + ' : ' + str(x) for x in moving_param]
    plt.legend(moving_param)
    plt.show()

if __name__ == '__main__':
    Nmc = 100
    N = 5
    T = 1
    t = 0
    K = 100
    r = 0.1
    vol = 0.2
    S0 = 100

    option1 = Option_prem_gen('Call Spread', 100, [95, 105], 0, T, r, vol)
    option2 = Option_prem_gen('Put Spread', 100, [95, 105], 0, T, r, vol)
    #option1.Delta_DF()
    print(option1.option_price_close_formulae())
    print(option2.option_price_close_formulae())

    print(option1.Delta_DF())
    print(option2.Delta_DF())
    print(option1.Theta_DF())
    print(option2.Theta_DF())

    # mean = random.random()
    # vol = random.random()

    # Option_eu('Call EU', 100, 95, 0, T, r, vol).display_payoff_option()
    # Option_eu('Put EU', 100, 95, 0, T, r, vol).display_payoff_option()
    # Option_eu('Call Spread', 100, 95, 0, T, r, vol, K_2=105).display_payoff_option()
    # print(Option_eu('Call Spread', 100, 95, 0, T, r, vol, K_2=105).option_price_close_formulae())


    vol = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    plot_greek_curves_2d('Call Spread', 'Delta', [95, 105], t, T, r, vol)
    plt.show()

    plot_greek_curves_2d('Call EU', 'Delta', K, t, T, r, vol)
    plt.show()
    plot_greek_curves_2d('Call EU', 'Gamma', K, t, T, r, vol)
    plt.show()
    plot_greek_curves_2d('Call EU', 'Vega', K, t, T, r, vol)
    plt.show()
    plot_greek_curves_2d('Call EU', 'Theta', K, t, T, r, vol)
    plt.show()

    r = 0.1
    plot_greek_curves_2d('Call EU', 'Theta', K, t, T, r, vol)
    plt.show()

    St = simu_actif(S0, N, t, T, 0.3, 0.80)
    #t = [t_/N for t_ in list(range(0, N, 1))]
    t = np.linspace(0, T-1.0*10**(-4), N+1)

    plt.plot(St)
    plt.title('Asset price')
    plt.show()
    price_ = [Option_eu('Call EU', St_, K, t_, T, r, vol).option_price_close_formulae() for t_, St_ in zip(t, St)]
    plt.plot(price_)
    plt.title('Option price')
    plt.show()
    deltas_ = [Option_eu('Call EU', St_, K, t_, T, r, vol).Delta_DF() for t_, St_ in zip(t, St)]
    plt.plot(deltas_)
    plt.title('Option delta')
    plt.show()
    gammas_ = [Option_eu('Call EU', St_, K, t_, T, r, vol).Gamma_DF() for t_, St_ in zip(t, St)]
    plt.plot(gammas_)
    plt.title('Option gamma')
    plt.show()
    thetas_ = [Option_eu('Call EU', St_, K, t_, T, r, vol).Theta_DF() for t_, St_ in zip(t, St)]
    plt.plot(thetas_)
    plt.title('Option theta')
    plt.show()
    vegas_ = [Option_eu('Call EU', St_, K, t_, T, r, vol).Vega_DF() for t_, St_ in zip(t, St)]
    plt.plot(vegas_)
    plt.title('Option vega')
    plt.show()

    #to activate the user interface
    # root = ThemedTk(theme="breeze")
    # root.mainloop()

      # Choose your preferred theme
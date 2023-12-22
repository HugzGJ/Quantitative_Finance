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
import yfinance as yf
import pandas as pd
from datetime import datetime
#
# from interest_rates import Tresury_bond_13weeks
# from interest_rates import Tresury_bond_5years
# from interest_rates import Tresury_bond_30years

class asset_BS():
    def __init__(self, S0, quantity):
        self.S0 = S0
        self.St = S0
        self.quantity = quantity
        self.history = [S0]
        self.mu = 0.1
        self.sigma = 0.2
        self.t = 0
    def simu_asset(self, T)->None:
        St = simu_actif(self.St, N, self.t, T, self.mu, self.sigma)
        St.pop(0)
        for st in St:
            self.history.append(st)
        self.St = self.history[-1]
    def pnl(self)->float:
        return self.St - self.S0
    def plot(self):
        plot_2d(list(range(len(self.history))), self.history, x_axis='t', y_axis='asset price', isShow=True)
    def Delta_DF(self):
        return 1*self.quantity
    def Gamma_DF(self):
        return 0
    def Vega_DF(self):
        return 0
    def Theta_DF(self):
        return 0
class Option_eu:
    #root parameter to
    def __init__(self, position, type, asset:(asset_BS), K, t, T, r, sigma, root=None):
        self.position = position
        self.asset = asset
        self.type = type
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

            self.asset.St_label = ttk.Label(self.frame, text="Current Stock Price:")
            self.asset.St_label.grid(row=2, column=0, sticky="w")

            self.asset.St_entry = ttk.Entry(self.frame)
            self.asset.St_entry.grid(row=2, column=1, pady=5)

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
            option_price = close_formulae_call_eu(self.asset.St, self.K, self.t, self.T, self.r, self.sigma)
            return self.position*option_price
        elif self.type == "Put EU":
            option_price = close_formulae_put_eu(self.asset.St, self.K, self.t, self.T, self.r, self.sigma)
            return self.position*option_price
        # elif self.type == "Call Spread":
        #     long_call = close_formulae_call_eu(self.asset.St, self.K, self.t, self.T, self.r, self.sigma)
        #     short_call = close_formulae_call_eu(self.asset.St, self.K_2, self.t, self.T, self.r, self.sigma)
        #     option_price = long_call - short_call
        #     return option_price
    def option_price_mc(self):
        prix_option = 0
        Nmc = 100000
        for i in range(Nmc):
            prix_actif = simu_actif(self.asset.St, self.K, self.t, self.T, self.r, self.sigma)
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
        return self.position*prix_option

    # def Delta(self):
    #     option_delta = (delta_option_eu(self.position, self.type, self.asset, self.K, self.t, self.T, self.r, self.sigma))
    #     return option_delta
    def Delta_DF(self):
        delta_St = 0.00001
        asset_delta = asset_BS(self.asset.St + delta_St, self.asset.quantity)
        option_delta_St = Option_eu(self.position, self.type, asset_delta, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.position, self.type,self.asset, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        delta = (option_delta_St - option_option)/delta_St
        return delta
    # def Gamma(self):
    #     option_gamma = (gamma_option_eu(self.position, self.type, self.asset, self.K, self.t, self.T, self.r, self.sigma))
    #     return option_gamma
    def Gamma_DF(self):
        delta_St = 0.00001
        asset_delta = asset_BS(self.asset.St + delta_St, self.asset.quantity)
        asset_delta_neg = asset_BS(self.asset.St - delta_St, self.asset.quantity)
        option_gamma_plus = Option_eu(self.position, self.type, asset_delta, self.K, self.t, self.T, self.r,
                                      self.sigma).option_price_close_formulae()
        option_gamma_minus = Option_eu(self.position, self.type, asset_delta_neg, self.K, self.t, self.T, self.r,
                                       self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.position, self.type,self.asset, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        gamma = ((option_gamma_plus + option_gamma_minus - 2 * option_option) / delta_St ** 2)
        return gamma
    def Vega_DF(self):
        delta_vol = 0.00001
        option_delta_vol = Option_eu(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                    self.sigma+delta_vol).option_price_close_formulae()
        option_option = Option_eu(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        vega = (option_delta_vol - option_option) / delta_vol
        return vega
    def Theta_DF(self):
        delta_t = 0.00001
        option_delta_t = Option_eu(self.position, self.type, self.asset, self.K, self.t+delta_t, self.T, self.r,
                                    self.sigma).option_price_close_formulae()
        option_option = Option_eu(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        theta = (option_delta_t - option_option) / delta_t
        return theta

    def simu_asset(self, time):
        self.asset.simu_asset(time)
        #self.asset.St = self.asset.history[-1]
        self.t = self.t + time


class Option_prem_gen(Option_eu):
    def __init__(self, position, type, asset:(asset_BS), K, t, T, r, sigma, root=None):
        self.position = position
        self.type = type
        self.asset = asset
        self.asset.St = asset.St
        self.K = K
        self.t = t
        self.T = T
        self.r = r
        self.sigma = sigma
        self.options =[]
        self.positions = []
        if type == "Call Spread":
            self.long_call = Option_eu(1, "Call EU", self.asset, self.K[0], self.t, self.T, self.r, self.sigma)
            self.short_call = Option_eu(-1, "Call EU", self.asset, self.K[1], self.t, self.T, self.r, self.sigma)
            self.options = [self.long_call, self.short_call]
            self.positions = [1, -1] #1 : long position, -1 : short position
            self.positions = [i*self.position for i in self.positions]
        if type == "Put Spread":
            self.long_put = Option_eu(1, "Put EU", self.asset, self.K[0], self.t, self.T, self.r, self.sigma)
            self.short_put = Option_eu(-1, "Put EU", self.asset, self.K[1], self.t, self.T, self.r, self.sigma)
            self.options = [self.long_put, self.short_put]
            self.positions = [1, -1]
            self.positions = [i*self.position for i in self.positions]

        if type == "Strangle":
            self.long_put = Option_eu(1, "Put EU", self.asset, self.K[0], self.t, self.T, self.r, self.sigma)
            self.long_call = Option_eu(1, "Call EU", self.asset, self.K[1], self.t, self.T, self.r, self.sigma)
            self.options = [self.long_put, self.long_call]
            self.positions = [1, 1] #1 : long position, -1 : short position
            self.positions = [i*self.position for i in self.positions]

    '''def option_price_close_formulae(self):
        if self.type == "Call Spread":
            Call1_price = self.long_call.option_price_close_formulae()
            Call2_price = self.short_call.option_price_close_formulae()
            return (Call1_price - Call2_price)'''

    def option_price_close_formulae(self):
        price_basket_options = 0
        for i in range(len(self.options)):
            price_basket_options+=self.positions[i]*self.options[i].option_price_close_formulae()
        return self.position*price_basket_options

    def Delta_DF(self):
        delta_St = 0.00001
        asset_delta = asset_BS(self.asset.St + delta_St, self.asset.quantity)
        option_delta_St = Option_prem_gen(self.position, self.type,asset_delta, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.position, self.type,self.asset, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        delta = (option_delta_St - option_option)/delta_St
        return delta
    def Gamma_DF(self):
        delta_St = 0.00001
        asset_delta = asset_BS(self.asset.St + delta_St, self.asset.quantity)
        asset_delta_neg = asset_BS(self.asset.St - delta_St, self.asset.quantity)

        option_gamma_plus = Option_prem_gen(self.position, self.type, asset_delta, self.K, self.t, self.T, self.r,
                                      self.sigma).option_price_close_formulae()
        option_gamma_minus = Option_prem_gen(self.position, self.type, asset_delta_neg, self.K, self.t, self.T, self.r,
                                       self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.position, self.type,self.asset, self.K, self.t, self.T, self.r, self.sigma).option_price_close_formulae()

        gamma = ((option_gamma_plus + option_gamma_minus - 2 * option_option) / delta_St ** 2)
        return gamma
    def Vega_DF(self):
        delta_vol = 0.00001
        option_delta_vol = Option_prem_gen(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                    self.sigma+delta_vol).option_price_close_formulae()
        option_option = Option_prem_gen(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        vega = (option_delta_vol - option_option) / delta_vol
        return vega
    def Theta_DF(self):
        delta_t = 0.00001
        option_delta_t = Option_prem_gen(self.position, self.type, self.asset, self.K, self.t+delta_t, self.T, self.r,
                                    self.sigma).option_price_close_formulae()
        option_option = Option_prem_gen(self.position, self.type, self.asset, self.K, self.t, self.T, self.r,
                                  self.sigma).option_price_close_formulae()

        theta = (option_delta_t - option_option) / delta_t
        return theta
    def simu_asset(self, time):
        self.asset.simu_asset(time)
        #self.asset.St = self.asset.history[-1]
        self.t = self.t + time
        for option in self.options:
            option.t = self.t

class Book():
    def __init__(self, options_basket:list)->None:
        self.basket = options_basket
        return
    def append(self, asset:(Option_eu, Option_prem_gen))->None:
        self.basket.append(asset)
        return
    #def remove(self, ):
    def option_price_close_formulae(self):
        return sum([option.option_price_close_formulae() if isinstance(option, (Option_eu, Option_prem_gen)) else 0 for option in self.basket])
    def Delta_DF(self):
        return sum([option.Delta_DF() for option in self.basket])
    def Gamma_DF(self):
        return sum([option.Gamma_DF() for option in self.basket])
    def Vega_DF(self):
        return sum([option.Vega_DF() for option in self.basket])
    def Theta_DF(self):
        return sum([option.Theta_DF() for option in self.basket])
    def simu_asset(self, time):
        list_asset = list(set([x.asset for x in self.basket]))
        for item in list_asset:
            item.simu_asset(time)
def plot_greek_curves_2d(position, type_option, greek, K, t_, T, r, vol):
    St_range = range(20, 180, 1)
    Eu_options = ['Call EU', 'Put EU']
    Option_first_gen = ['Call Spread', 'Put Spread', 'Strangle']
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
            asset = asset_BS(i, 0)
            option_obj = Option(position, type_option, asset, K, t_, T, r, vol)
            greek_list.append(option_obj.greek())
        #greek_list = [i*position for i in greek_list]
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
            asset = asset_BS(i, 0)
            option_obj = Option(position, type_option, asset, K, t_, T, r, vol)
            greek_list.append(option_obj.greek())
        greek_list = [i*position for i in greek_list]
        plot_2d(St_range, greek_list, f"{greek} curve - {type_option}", "Prix de l'actif", greek, False)
    moving_param = [moving_param_label + ' : ' + str(x) for x in moving_param]
    plt.legend(moving_param)
    plt.show()

def Volatilite_implicite(stock_name, maturity_date, option_type, r, plot=True):
    t = 0
    epsilon = 0.0001
    maturity = pd.Timestamp(maturity_date) - datetime.now()
    T = maturity.days / 365.6
    stock_obj = yf.Ticker(stock_name)
    options = stock_obj.option_chain(maturity_date)
    S0 = stock_obj.history().tail(1)['Close'].values[0]
    if option_type == "Call EU":
        options = options.calls
    elif option_type == "Put EU":
        options = options.puts
    options_df = options[['lastTradeDate', 'strike', 'bid', 'impliedVolatility']]

    vol_implicite = []
    strikes = []
    for i in range(len(options_df)):
        if options_df['bid'].iloc[i] < S0 and options_df['bid'].iloc[i] > max(S0 - options_df['strike'].iloc[i] * np.exp(-r * T), 0):
            sigma = np.sqrt(2 * np.abs(np.log(r * T + S0 / options_df['strike'].iloc[i])) / T)
            option_eu_obj = Option_eu(Book, option_type, S0, options_df['strike'].iloc[i], t, T, r, sigma)
            Market_price = options_df['bid'].iloc[i]
            # Algorithme de Newton :
            while np.abs(option_eu_obj.option_price_close_formulae() - Market_price) > epsilon:
                sigma = sigma - (option_eu_obj.option_price_close_formulae() - Market_price) / option_eu_obj.Vega_DF()
                option_eu_obj = Option_eu(Book, option_type, S0, options_df['strike'].iloc[i], t, T, r, sigma)

            strikes.append(options_df['strike'].iloc[i])
            vol_implicite.append(sigma)

    plot_2d(strikes, vol_implicite, 'Volatility smile', 'Strike', 'Implied volatility', isShow=plot, legend=maturity_dates)
    result = dict(zip(strikes, vol_implicite))
    return result
if __name__ == '__main__':
    Nmc = 100
    N = 5
    T = 1
    t = 0
    K = 100
    vol = 0.2
    S0 = 100
    r = 0.1
    # maturity_date = '2024-02-16'
    # maturity_dates = ['2023-12-15', '2023-12-22', '2023-12-29', '2024-05-01', '2024-12-01', '2025-12-01']
    # stock = 'AAPL'
    # r = Tresury_bond_13weeks
    # for maturity_date in maturity_dates:
    #     implied_vol_dict = Volatilite_implicite(stock, maturity_date, 'Call EU', r, False)
    # plt.show()
    # for maturity_date in maturity_dates:
    #     implied_vol_dict = Volatilite_implicite(stock, maturity_date, 'Put EU', r, False)
    # plt.show()
    # print(Tresury_bond_13weeks)
    #
    # callEU = Option_eu(1, 'Call EU', 100, 95, 0, T, r, vol)
    # PutEU = Option_eu(1, 'Put EU', 100, 95, 0, T, r, vol)
    #
    # plot_greek_curves_2d(1, 'Strangle', 'Delta', [50, 120], t, T, r, vol)
    # plt.show()
    #
    # position1.append(PutEU)
    T = 2
    stock1 = asset_BS(100, 0)
    callEU = Option_eu(1, 'Call EU', stock1, 95, 0, T, r, vol)
    callEU2 = Option_eu(-2, 'Call EU', stock1, 135, 0, T, r, vol)

    book1 = Book([callEU, callEU2])
    book1.simu_asset(1)
    strangle = Option_prem_gen(-1, 'Strangle', stock1, [95, 105], 0, T, r, vol)

    print('book greeks')
    print(book1.Delta_DF())
    print(book1.Gamma_DF())
    print(book1.Theta_DF())
    print(f'book price = {book1.option_price_close_formulae()}')
    print(f'stock price = {book1.basket[0].St}')
    book1.simu_asset(1)
    print('asset evolution done')
    print(f'book price = {book1.option_price_close_formulae()}')
    print(f'stock price = {book1.basket[0].St}')
    print(book1.Delta_DF())
    print(book1.Gamma_DF())
    print(book1.Theta_DF())

    plot_greek_curves_2d(-1, 'Call EU', 'Theta', 95, t, T, r, vol)
    plt.show()

    straddle = Option_prem_gen(1, 'Strangle', stock1, [95, 95], 0, T, r, vol)

    straddle.option_price_close_formulae()
    stock1.simu_asset(1)

    T = [0.1, 0.2, 1]

    plot_greek_curves_2d(-1, 'Strangle', 'Delta', [50, 120], t, T, r, vol)
    plt.show()
    plot_greek_curves_2d(-1,'Strangle', 'Gamma', [50, 120], t, T, r, vol)
    plt.show()
    plot_greek_curves_2d(-1,'Strangle', 'Vega', [50, 120], t, T, r, vol)
    plt.show()
    plot_greek_curves_2d(-1,'Strangle', 'Theta', [50, 120], t, T, r, vol)
    plt.show()
    #to activate the user interface
    # root = ThemedTk(theme="breeze")
    # root.mainloop()

      # Choose your preferred theme

    #to activate the user interface
    # root = ThemedTk(theme="breeze")
    # root.mainloop()

      # Choose your preferred theme
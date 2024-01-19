from Asset_class import asset_BS
from Graphics import plot_2d
from Options_class import  Option_eu, Option_prem_gen

class Book():
    def __init__(self, options_basket:list, asset=None)->None:
        self.basket = options_basket
        self.asset = asset
        return
    def append(self, option:(Option_eu, Option_prem_gen))->None:
        self.basket.append(option)
        return
    def delta_hedge(self, asset:asset_BS):
        if not isinstance(asset, asset_BS):
            raise TypeError("asset must be of type asset_BS")
        self.asset = asset
        return
    #def remove(self, ):
    def option_price_close_formulae(self):
        return sum([option.option_price_close_formulae() if isinstance(option, (Option_eu, Option_prem_gen)) else 0 for option in self.basket])
    def get_payoff_option(self, ST:int):
        payoff = 0
        for option in self.basket:
            payoff+=option.get_payoff_option(ST)
        return payoff
    def display_payoff_option(self):
        K_min = 99999999
        K_max = -99999999
        for option in self.basket:
            if type(option.K) == list:
                K_min_temp = min(option.K)
                K_max_temp = max(option.K)
            else:
                K_min_temp = option.K
                K_max_temp = option.K

            if K_min_temp < K_min:
                K_min = K_min_temp
            if K_max_temp > K_max:
                K_max = K_max_temp
        start = K_min*0.5
        end = K_max*1.5
        ST = list(range(round(start), round(end)))
        payoffs = []
        for i in ST:
            payoffs.append(self.get_payoff_option(i))
        plot_2d(ST, payoffs, "Payoff of the book", "Asset price", "Payoff", isShow=True)
    def Delta_DF(self):
        hedge = self.asset.quantity if self.asset != None else 0
        return sum([option.Delta_DF() for option in self.basket]) + hedge
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
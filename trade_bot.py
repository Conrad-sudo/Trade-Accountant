from tkinter import *
from pandastable import Table
import trans_func
import pandas as pd
from datetime import datetime


root= Tk()
root.title('SERAL Balance Book')
root.geometry('1850x855')

# make app width,height resizable
root.resizable(True,True)
root.grid_columnconfigure(index=0,weight=1)
root.grid_columnconfigure(index=1,weight=1)
root.grid_columnconfigure(index=2,weight=1)
root.grid_columnconfigure(index=3,weight=1)

root.grid_rowconfigure(index=0,weight=1)
root.grid_rowconfigure(index=1,weight=1)
root.grid_rowconfigure(index=2,weight=1)
root.grid_rowconfigure(index=3,weight=1)
root.grid_rowconfigure(index=4,weight=1)
root.grid_rowconfigure(index=5,weight=1)
root.grid_rowconfigure(index=6,weight=1)
root.grid_rowconfigure(index=7,weight=1)
root.grid_rowconfigure(index=8,weight=1)
root.grid_rowconfigure(index=9,weight=1)
root.grid_rowconfigure(index=10,weight=1)
root.grid_rowconfigure(index=12,weight=1)
root.grid_rowconfigure(index=13,weight=1)


def fetch_balance():

    market_choices = []
    exchange_choices = []
    quote=quote_pick.get()



    try:
        split_time=from_year.get().split('/')
        f_year=int(split_time[0])
        f_month=int(split_time[1])
        f_day=int(split_time[2])
        f_hour=int(split_time[3])
        f_minute=int(split_time[4])

        split_time = to_year.get().split('/')
        t_year = int(split_time[0])
        t_month = int(split_time[1])
        t_day = int(split_time[2])
        t_hour = int(split_time[3])
        t_minute = int(split_time[4])


        from_time= datetime(year=f_year,month=f_month,day=f_day,hour=f_hour,minute=f_minute)
        to_time= datetime(year=t_year,month=t_month,day=t_day,hour=t_hour,minute=t_minute)

        from_time=from_time.timestamp()*1000
        to_time=to_time.timestamp()*1000
        now_time=int(datetime.now().timestamp())*1000



    except ValueError:
        error_label.configure(text='')
        error_label.configure(text='Lütfen doğru zaman formatı girin')

    except TypeError:
        error_label.configure(text='')
        error_label.configure(text='Zaman için sadece sayı girin')





    #Get markets
    # Create the reordered pair list by taking the ones that are not empty and combining them with the quote string

    for base in bases:
        if base.get() != '':
            market_choices.append(base.get() +quote)


    #Get exchanges
    # Get eh chosen exchanges
    for p in exchange_list:
        if p.get() != '':
            exchange_choices.append(p.get())

    #Incase there are no exchanges
    if len(exchange_choices)==0 or len(market_choices)==0:
        error_label.configure(text='')
        error_label.configure(text='Lütfen Base,Quote ve Borsa seçin')


    else:
        for market in market_choices:

            # Get the dataframe

            if to_time>from_time and to_time<=now_time:
                data_frame = trans_func.get_balance(market=market, exchange=exchange_choices, since_date=from_time,to_date=to_time)
            elif to_time<from_time or to_time>now_time:
                error_label.configure(text='')
                error_label.configure(text='Zaman aralığı geçersiz')

            if type(data_frame) == str:
                error_label.configure(text=data_frame)

            else:
                error_label.configure(text='')
                # Create a window
                window = Tk()
                window.title(market)
                # Create a frame
                frame = Frame(window)
                frame.pack()
                # Create a table
                table = Table(frame, dataframe=data_frame, height=300, width=1500)
                table.show()


def fetch_excel():

    market_choices = []
    exchange_choices = []
    balance_dict={}
    quote = quote_pick.get()


    #Check if the time was entered
    try:
        split_time = from_year.get().split('/')
        f_year = int(split_time[0])
        f_month = int(split_time[1])
        f_day = int(split_time[2])
        f_hour = int(split_time[3])
        f_minute = int(split_time[4])

        split_time = to_year.get().split('/')
        t_year = int(split_time[0])
        t_month = int(split_time[1])
        t_day = int(split_time[2])
        t_hour = int(split_time[3])
        t_minute = int(split_time[4])

        from_time = datetime(year=f_year, month=f_month, day=f_day, hour=f_hour, minute=f_minute)
        to_time = datetime(year=t_year, month=t_month, day=t_day, hour=t_hour, minute=t_minute)

        from_time = from_time.timestamp()*1000
        to_time = to_time.timestamp()*1000
        now_time=int(datetime.now().timestamp())*1000



    except ValueError :
        error_label.configure(text='')
        error_label.configure(text='Lütfen doğru zaman formatı girin')

    except IndexError:
        error_label.configure(text='')
        error_label.configure(text='Lütfen sadece sayı girin')

    #Get markets
    # Create the reordered pair list by taking the ones that are not empty and combining them with the quote string
    for base in bases:
        if base.get() != '':
            market_choices.append(base.get() + quote)

    #Get exchanges
    # Get the chosen exchanges
    for exchange in exchange_list:
        if exchange.get() != '':
            exchange_choices.append(exchange.get())


    if len(exchange_choices)==0 or len(market_choices)==0:
        error_label.configure(text='')
        error_label.configure(text='Lütfen Base,Quote ve Borsa seçin')

    else:
        for market in market_choices:

            if to_time>from_time and to_time<=now_time:
                df = trans_func.get_balance(market=market, exchange=exchange_choices, since_date=from_time,to_date=to_time)
            elif to_time<from_time or to_time>now_time:
                error_label.configure(text='')
                error_label.configure(text='Zaman aralığı geçersiz')


            if type(df) == str:
                break
            else:
                balance_dict.update({market: df})

        if len(balance_dict) != 0:
            with pd.ExcelWriter('Balance_Sheet.xlsx') as writer:
                for market in balance_dict:
                    check = market.split('/')
                    new_market = check[0] + '-' + check[1]
                    balance_dict[market].to_excel(writer, sheet_name=f'{new_market}', index=False)

            error_label.configure(text='')
            error_label.configure(text='Export başarılı')
            root.after(5000,clear)


        elif len(balance_dict) == 0:
            error_label.configure(text='')
            error_label.configure(text=f'{market_choices} mevcut değil ')


def reset_from(*args):
    from_year.delete(0, END)
    from_year.insert(0,'2022/')


def reset_to(*args):
    to_year.delete(0, END)
    to_year.insert(0, '2022/')


def clear():
    error_label.configure(text='')


#rates_frame=Frame(root)
#rates_frame.grid(row=0, column=0, sticky='nsew' )

#Rates label
rates_label_1=Label(root, text='',height=2, background='black', foreground='white')
rates_label_1.grid(row=0,column=0,sticky='nsew',pady=(0,15))
rates_label_2=Label(root, text='',height=2, background='black',foreground='white')
rates_label_2.grid(row=0,column=1,sticky='nsew',pady=(0,15))
rates_label_3=Label(root, text='',height=2, background='black',foreground='white')
rates_label_3.grid(row=0,column=2,sticky='nsew',pady=(0,15))
rates_label_4=Label(root, text='',height=2, background='black',foreground='white')
rates_label_4.grid(row=0,column=3,sticky='nsew',pady=(0,15))



#Configure frames for each panel section

base_frame=Frame(root)
base_frame.grid(row=1, column=0, sticky='nsew')

check_button_frame=Frame(root)
check_button_frame.grid(row=2, column=0, sticky='nsew' )

quote_frame=Frame(root)
quote_frame.grid(row=3, column=0, sticky='nsew')

quote_button_frame=Frame(root)
quote_button_frame.grid(row=4, column=0, sticky='nsew')


exchange_frame=Frame(root)
exchange_frame.grid(row=6, column=0, sticky='nsew')

exchange_button_frame=Frame(root)
exchange_button_frame.grid(row=7, column=0, sticky='nsew')

time_frame=Frame(root)
time_frame.grid(row=8, column=0, sticky='nsew',pady=(10,0), ipady=10)

time_label_frame=Frame(root)
time_label_frame.grid(row=9, column=0, sticky='nsew',ipady=20)

error_frame=Frame(root)
error_frame.grid(row=10,column=0,sticky='nsew')

button_frame=Frame(root)
button_frame.grid(row=11,column=0,sticky='nsew')



#Settings lable
#title= Label(market_frame, text='Borsalar', font=('Arial',25,'italic'), fg='red', ).grid(row=3,column=0,sticky='w', pady=(40,0), padx=10)

#Subheading
subheading_1= Label(base_frame, text='Base seçin', font=('Arial',15,'bold'), fg='#7A796E' ,pady=20, padx=10).grid(row=4,column=0, sticky='w')


#Declare variables
btc=StringVar()
eth=StringVar()
xrp=StringVar()
ltc=StringVar()
usdt=StringVar()
link=StringVar()
atom=StringVar()
trx=StringVar()
dot=StringVar()
uni=StringVar()
mkr=StringVar()
enj=StringVar()
omg=StringVar()
comp=StringVar()
grt=StringVar()
mana=StringVar()
matic=StringVar()
snx=StringVar()
bat=StringVar()
avax=StringVar()
doge=StringVar()
chz=StringVar()
sol=StringVar()
axs=StringVar()
shib=StringVar()
ftm=StringVar()
lrc=StringVar()
storj=StringVar()
aave=StringVar()
gala=StringVar()
sand=StringVar()
audio=StringVar()
spell=StringVar()
luna=StringVar()
algo= StringVar()
ape=StringVar()
bnt=StringVar()
crv=StringVar()
skl=StringVar()
usdc=StringVar()
xlm=StringVar()
eos=StringVar()
xtz=StringVar()
dash=StringVar()
ada=StringVar()
ankr=StringVar()
uma=StringVar()
nu= StringVar()
poly=StringVar()
amp=StringVar()
qnt=StringVar()
bch=StringVar()
inch=StringVar()
ksm=StringVar()
xmr=StringVar()
sushi=StringVar()
mir=StringVar()
yfi=StringVar()
near=StringVar()
qtum=StringVar()
rune=StringVar()
badger=StringVar()
etc=StringVar()
cro=StringVar()
lunc=StringVar()


#Declare Exchange buttons
ftx_main=StringVar()
ftx_btc=StringVar()
ftx_eth=StringVar()
ftx_sol=StringVar()
ftx_tether=StringVar()
ftx_yedek=StringVar()
coinbase=StringVar()
kraken=StringVar()
bitfinex=StringVar()

#Put variables into a list for selection
bases=[btc,eth,xrp,ltc,usdt,link,atom,trx,dot,uni,mkr,enj,omg,comp,grt,mana,matic,snx,bat,avax,doge,chz,sol,axs,shib,ftm,lrc,
       storj,aave,gala,sand,audio,spell,luna,algo,ape,bnt,crv,skl,usdc,xlm,eos,xtz,dash,ada,ankr,uma,nu,poly,amp,qnt,bch,inch,ksm,xmr,sushi,mir,yfi,near,qtum,rune,badger,etc,cro,lunc]

exchange_list=[ftx_sol,ftx_yedek,ftx_tether,ftx_eth,ftx_btc,ftx_main,coinbase,kraken,bitfinex]

#Declare Checkbuttons

y_padding=5

# 1st row
btc_check=Checkbutton(check_button_frame,variable=btc,onvalue='BTC',offvalue='',width=10, text= 'BTC', font=('Arial',10,'normal')).grid(row=0,column=0,sticky='w',padx=10,pady=y_padding)
usdt_check=Checkbutton(check_button_frame,variable=usdt,onvalue='USDT',offvalue='',width=10, text= 'USDT', font=('Arial',10,'normal')).grid(row=0,column=1,sticky='w',padx=10,pady=y_padding)
aave_check=Checkbutton(check_button_frame,variable=aave,onvalue='AAVE',offvalue='',width=10, text= 'AAVE', font=('Arial',10,'normal')).grid(row=0,column=2,sticky='w',padx=10,pady=y_padding)
usdc_check=Checkbutton(check_button_frame,variable=usdc,onvalue='USDC',offvalue='',width=10, text= 'USDC', font=('Arial',10,'normal')).grid(row=0,column=3,sticky='w',padx=10,pady=y_padding)
xlm_check=Checkbutton(check_button_frame,variable=xlm,onvalue='XLM',offvalue='',width=10, text= 'XLM', font=('Arial',10,'normal')).grid(row=0,column=4,sticky='w',padx=10,pady=y_padding)
eth_chek=Checkbutton(check_button_frame,variable=eth,onvalue='ETH',offvalue='',width=10, text= 'ETH', font=('Arial',10,'normal')).grid(row=0,column=5,sticky='w',padx=10,pady=y_padding)
link_check=Checkbutton(check_button_frame,variable=link,onvalue='LINK',offvalue='',width=10, text= 'LINK', font=('Arial',10,'normal')).grid(row=0,column=6,sticky='w',padx=10,pady=y_padding)
luna_check=Checkbutton(check_button_frame,variable=luna,onvalue='LUNA',offvalue='',width=10, text= 'LUNA', font=('Arial',10,'normal')).grid(row=0,column=7,sticky='w',padx=10,pady=y_padding)
eos_check=Checkbutton(check_button_frame,variable=eos,onvalue='EOS',offvalue='',width=10, text= 'EOS', font=('Arial',10,'normal')).grid(row=0,column=8,sticky='w',padx=10,pady=y_padding)
lunc_check=Checkbutton(check_button_frame,variable=lunc,onvalue='LUNC',offvalue='',width=10, text= 'LUNC', font=('Arial',10,'normal')).grid(row=0,column=9,sticky='w',padx=10,pady=y_padding)
xrp_check=Checkbutton(check_button_frame,variable=xrp,onvalue='XRP',offvalue='',width=10, text= 'XRP', font=('Arial',10,'normal')).grid(row=0,column=10,sticky='w',padx=10,pady=y_padding)
atom_check=Checkbutton(check_button_frame,variable=atom,onvalue='ATOM',offvalue='',width=10, text= 'ATOM', font=('Arial',10,'normal')).grid(row=0,column=11,sticky='w',padx=10,pady=y_padding)
storj_check=Checkbutton(check_button_frame,variable=storj,onvalue='STORJ',offvalue='',width=10, text= 'STORJ', font=('Arial',10,'normal')).grid(row=0,column=12,sticky='w',padx=10,pady=y_padding)

#2nd row
xtz_check=Checkbutton(check_button_frame,variable=xtz,onvalue='XTZ',offvalue='',width=10, text= 'XTZ', font=('Arial',10,'normal')).grid(row=1,column=0,sticky='w',padx=10,pady=y_padding)
dash_check=Checkbutton(check_button_frame,variable=dash,onvalue='DASH',offvalue='',width=10, text= 'DASH', font=('Arial',10,'normal')).grid(row=1,column=1,sticky='w',padx=10,pady=y_padding)
ltc_check=Checkbutton(check_button_frame,variable=ltc,onvalue='LTC',offvalue='',width=10, text= 'LTC', font=('Arial',10,'normal')).grid(row=1,column=2,sticky='w',padx=10,pady=y_padding)
trx_check=Checkbutton(check_button_frame,variable=trx,onvalue='TRX',offvalue='',width=10, text= 'TRX', font=('Arial',10,'normal')).grid(row=1,column=3,sticky='w',padx=10,pady=y_padding)
spell_check=Checkbutton(check_button_frame,variable=spell,onvalue='SPELL',offvalue='',width=5, text= 'SPELL', font=('Arial',10,'normal')).grid(row=1,column=4,sticky='w',padx=10,pady=y_padding)
ada_check=Checkbutton(check_button_frame,variable=ada,onvalue='ADA',offvalue='',width=10, text= 'ADA', font=('Arial',10,'normal')).grid(row=1,column=5,sticky='w',padx=10,pady=y_padding)
ankr_check=Checkbutton(check_button_frame,variable=ankr,onvalue='ANKR',offvalue='',width=10, text= 'ANKR', font=('Arial',10,'normal')).grid(row=1,column=6,sticky='w',padx=10,pady=y_padding)
dot_check=Checkbutton(check_button_frame,variable=dot,onvalue='DOT',offvalue='',width=10, text= 'DOT', font=('Arial',10,'normal')).grid(row=1,column=7,sticky='w',padx=10,pady=y_padding)
omg_check=Checkbutton(check_button_frame,variable=omg,onvalue='OMG',offvalue='',width=10, text= 'OMG', font=('Arial',10,'normal')).grid(row=1,column=8,sticky='w',padx=10,pady=y_padding)
enj_check=Checkbutton(check_button_frame,variable=enj,onvalue='ENJ',offvalue='',width=10, text= 'ENJ', font=('Arial',10,'normal')).grid(row=1,column=9,sticky='w',padx=10,pady=y_padding)
uma_check=Checkbutton(check_button_frame,variable=uma,onvalue='UMA',offvalue='',width=10, text= 'UMA', font=('Arial',10,'normal')).grid(row=1,column=10,sticky='w',padx=10,pady=y_padding)
nu_check=Checkbutton(check_button_frame,variable=nu,onvalue='NU',offvalue='',width=10, text= 'NU', font=('Arial',10,'normal')).grid(row=1,column=11,sticky='w',padx=10,pady=y_padding)
uni_check=Checkbutton(check_button_frame,variable=uni,onvalue='UNI',offvalue='',width=10, text= 'UNI', font=('Arial',10,'normal')).grid(row=1,column=12,sticky='w',padx=10,pady=y_padding)


#3rd row
comp_check=Checkbutton(check_button_frame,variable=comp,onvalue='COMP',offvalue='',width=10, text= 'COMP', font=('Arial',10,'normal')).grid(row=2,column=0,sticky='w',padx=10,pady=y_padding)
mana_check=Checkbutton(check_button_frame,variable=mana,onvalue='MANA',offvalue='',width=10, text= 'MANA', font=('Arial',10,'normal')).grid(row=2,column=1,sticky='w',padx=10,pady=y_padding)
poly_check=Checkbutton(check_button_frame,variable=poly,onvalue='POLY',offvalue='',width=10, text= 'POLY', font=('Arial',10,'normal')).grid(row=2,column=2,sticky='w',padx=10,pady=y_padding)
amp_check=Checkbutton(check_button_frame,variable=amp,onvalue='AMP',offvalue='',width=10, text= 'AMP', font=('Arial',10,'normal')).grid(row=2,column=3,sticky='w',padx=10,pady=y_padding)
mkr_check=Checkbutton(check_button_frame,variable=mkr,onvalue='MKR',offvalue='',width=10, text= 'MKR', font=('Arial',10,'normal')).grid(row=2,column=4,sticky='w',padx=10,pady=y_padding)
grt_check=Checkbutton(check_button_frame,variable=grt,onvalue='GRT',offvalue='',width=10, text= 'GRT', font=('Arial',10,'normal')).grid(row=2,column=5,sticky='w',padx=10,pady=y_padding)
lrc_check=Checkbutton(check_button_frame,variable=lrc,onvalue='LRC',offvalue='',width=10, text= 'LRC', font=('Arial',10,'normal')).grid(row=2,column=6,sticky='w',padx=10,pady=y_padding)
qnt_check=Checkbutton(check_button_frame,variable=qnt,onvalue='QNT',offvalue='',width=10, text= 'QNT', font=('Arial',10,'normal')).grid(row=2,column=7,sticky='w',padx=10,pady=y_padding)
bch_check=Checkbutton(check_button_frame,variable=bch,onvalue='BCH',offvalue='',width=10, text= 'BCH', font=('Arial',10,'normal')).grid(row=2,column=8,sticky='w',padx=10,pady=y_padding)
matic_check=Checkbutton(check_button_frame,variable=matic,onvalue='MATIC',offvalue='',width=10, text= 'MATIC', font=('Arial',10,'normal')).grid(row=2,column=9,sticky='w',padx=10,pady=y_padding)
doge_check=Checkbutton(check_button_frame,variable=doge,onvalue='DOGE',offvalue='',width=10, text= 'DOGE', font=('Arial',10,'normal')).grid(row=2,column=10,sticky='w',padx=10,pady=y_padding)
audio_check=Checkbutton(check_button_frame,variable=audio,onvalue='AUDIO',offvalue='',width=10, text= 'AUDIO', font=('Arial',10,'normal')).grid(row=2,column=11,sticky='w',padx=10,pady=y_padding)
inch_check=Checkbutton(check_button_frame,variable=inch,onvalue='1INCH',offvalue='',width=10, text= '1INCH', font=('Arial',10,'normal')).grid(row=2,column=12,sticky='w',padx=10,pady=y_padding)

#4th row
ksm_check=Checkbutton(check_button_frame,variable=ksm,onvalue='KSM',offvalue='',width=10, text= 'KSM', font=('Arial',10,'normal')).grid(row=3,column=0,sticky='w',padx=10,pady=y_padding)
snx_check=Checkbutton(check_button_frame,variable=snx,onvalue='SNX',offvalue='',width=10, text= 'SNX', font=('Arial',10,'normal')).grid(row=3,column=1,sticky='w',padx=10,pady=y_padding)
chz_check=Checkbutton(check_button_frame,variable=chz,onvalue='CHZ',offvalue='',width=10, text= 'CHZ', font=('Arial',10,'normal')).grid(row=3,column=2,sticky='w',padx=10,pady=y_padding)
algo_check=Checkbutton(check_button_frame,variable=algo,onvalue='ALGO',offvalue='',width=10, text= 'ALGO', font=('Arial',10,'normal')).grid(row=3,column=3,sticky='w',padx=10,pady=y_padding)
xmr_check=Checkbutton(check_button_frame,variable=xmr,onvalue='XMR',offvalue='',width=10, text= 'XMR', font=('Arial',10,'normal')).grid(row=3,column=4,sticky='w',padx=10,pady=y_padding)
sushi_check=Checkbutton(check_button_frame,variable=sushi,onvalue='SUSHI',offvalue='',width=10, text= 'SUSHI', font=('Arial',10,'normal')).grid(row=3,column=5,sticky='w',padx=10,pady=y_padding)
bat_check=Checkbutton(check_button_frame,variable=bat,onvalue='BAT',offvalue='',width=10, text= 'BAT', font=('Arial',10,'normal')).grid(row=3,column=6,sticky='w',padx=10,pady=y_padding)
sol_check=Checkbutton(check_button_frame,variable=sol,onvalue='SOL',offvalue='',width=10, text= 'SOL', font=('Arial',10,'normal')).grid(row=3,column=7,sticky='w',padx=10,pady=y_padding)
ape_check=Checkbutton(check_button_frame,variable=ape,onvalue='APE',offvalue='',width=10, text= 'APE', font=('Arial',10,'normal')).grid(row=3,column=8,sticky='w',padx=10,pady=y_padding)
mir_check=Checkbutton(check_button_frame,variable=mir,onvalue='MIR',offvalue='',width=10, text= 'MIR', font=('Arial',10,'normal')).grid(row=3,column=9,sticky='w',padx=10,pady=y_padding)
yfi_check=Checkbutton(check_button_frame,variable=yfi,onvalue='YFI',offvalue='',width=10, text= 'YFI', font=('Arial',10,'normal')).grid(row=3,column=10,sticky='w',padx=10,pady=y_padding)
avax_check=Checkbutton(check_button_frame,variable=avax,onvalue='AVAX',offvalue='',width=10, text= 'AVAX', font=('Arial',10,'normal')).grid(row=3,column=11,sticky='w',padx=10,pady=y_padding)
axs_check=Checkbutton(check_button_frame,variable=axs,onvalue='AXS',offvalue='',width=10, text= 'AXS', font=('Arial',10,'normal')).grid(row=3,column=12,sticky='w',padx=10,pady=y_padding)


#5th row
bnt_check=Checkbutton(check_button_frame,variable=bnt,onvalue='BNT',offvalue='',width=10, text= 'BNT', font=('Arial',10,'normal')).grid(row=4,column=0,sticky='w',padx=10,pady=y_padding)
near_check=Checkbutton(check_button_frame,variable=near,onvalue='NEAR',offvalue='',width=10, text= 'NEAR', font=('Arial',10,'normal')).grid(row=4,column=1,sticky='w',padx=10,pady=y_padding)
qtum_check=Checkbutton(check_button_frame,variable=qtum,onvalue='QTUM',offvalue='',width=10, text= 'QTUM', font=('Arial',10,'normal')).grid(row=4,column=2,sticky='w',padx=10,pady=y_padding)
shib_check=Checkbutton(check_button_frame,variable=shib,onvalue='SHIB',offvalue='',width=10, text= 'SHIB', font=('Arial',10,'normal')).grid(row=4,column=3,sticky='w',padx=10,pady=y_padding)
gala_check=Checkbutton(check_button_frame,variable=gala,onvalue='GALA',offvalue='',width=10, text= 'GALA', font=('Arial',10,'normal')).grid(row=4,column=4,sticky='w',padx=10,pady=y_padding)
crv_check=Checkbutton(check_button_frame,variable=crv,onvalue='CRV',offvalue='',width=10, text= 'CRV', font=('Arial',10,'normal')).grid(row=4,column=5,sticky='w',padx=10,pady=y_padding)
rune_check=Checkbutton(check_button_frame,variable=rune,onvalue='RUNE',offvalue='',width=10, text= 'RUNE', font=('Arial',10,'normal')).grid(row=4,column=6,sticky='w',padx=10,pady=y_padding)
badger_check=Checkbutton(check_button_frame,variable=badger,onvalue='BADGER',offvalue='',width=10, text= 'BADGER', font=('Arial',10,'normal')).grid(row=4,column=7,sticky='w',padx=10,pady=y_padding)
ftm_check=Checkbutton(check_button_frame,variable=ftm,onvalue='FTM',offvalue='',width=10, text= 'FTM', font=('Arial',10,'normal')).grid(row=4,column=8,sticky='w',padx=10,pady=y_padding)
sand_check=Checkbutton(check_button_frame,variable=sand,onvalue='SAND',offvalue='',width=10, text= 'SAND', font=('Arial',10,'normal')).grid(row=4,column=9,sticky='w',padx=10,pady=y_padding)
skl_check=Checkbutton(check_button_frame,variable=skl,onvalue='SKL',offvalue='',width=10, text= 'SKL', font=('Arial',10,'normal')).grid(row=4,column=10,sticky='w',padx=10,pady=y_padding)
etc_check=Checkbutton(check_button_frame,variable=etc,onvalue='ETC',offvalue='',width=10, text= 'ETC', font=('Arial',10,'normal')).grid(row=4,column=11,sticky='w',padx=10,pady=y_padding)
cro_check=Checkbutton(check_button_frame,variable=cro,onvalue='CRO',offvalue='',width=10, text= 'CRO', font=('Arial',10,'normal')).grid(row=4,column=12,sticky='w',padx=10,pady=y_padding)



#Quote label
quote_label= Label(quote_frame,text='Quote seçin',font=('Arial',15,'bold'), fg='#7A796E').grid(row=7, column=0,pady=(30,20), padx=(10,0) , sticky='w')
quote_pick=StringVar()

#Quote button
quote_usd=Checkbutton(quote_button_frame,variable=quote_pick, onvalue='/USD', offvalue='', text='USD', width=12,font=('Arial',13,'bold')).grid(row=8,column=0)
quote_usdt=Checkbutton(quote_button_frame,variable=quote_pick, onvalue='/USDT', offvalue='', text='USDT', width=12,font=('Arial',13,'bold')).grid(row=8,column=1)
quote_euro=Checkbutton(quote_button_frame,variable=quote_pick, onvalue='/USDC', offvalue='', text='USDC', width=12,font=('Arial',13,'bold')).grid(row=8,column=2)



#Exchange label
ask_scenario_label= Label(exchange_frame,text='Borsa seçin',font=('Arial',15,'bold'), fg='#7A796E').grid(row=9, column=0,pady=(30,20),padx=10, sticky='w')
ask_scenario_pick =StringVar()

# Exchange Buttons
ftx_main_check=Checkbutton(exchange_button_frame,variable=ftx_main, onvalue='ftx_main', offvalue='', text='FTX Main', width=12,font=('Arial',13,'bold')).grid(row=10,column=0)
ftx_btc_check=Checkbutton(exchange_button_frame,variable=ftx_btc, onvalue='ftx_btc', offvalue='', text='FTX BTC', width=12,font=('Arial',13,'bold')).grid(row=10,column=1)
ftx_eth_check=Checkbutton(exchange_button_frame,variable=ftx_eth, onvalue='ftx_eth', offvalue='', text='FTX ETH', width=12,font=('Arial',13,'bold')).grid(row=10,column=2)
ftx_sol_check=Checkbutton(exchange_button_frame,variable=ftx_sol, onvalue='ftx_sol', offvalue='', text='FTX SOL', width=12,font=('Arial',13,'bold')).grid(row=11,column=0)
ftx_tether_check=Checkbutton(exchange_button_frame,variable=ftx_tether, onvalue='ftx_tether', offvalue='', text='FTX Tether', width=12,font=('Arial',13,'bold')).grid(row=11,column=1)
ftx_yedek_check=Checkbutton(exchange_button_frame,variable=ftx_yedek, onvalue='ftx_yedek', offvalue='', text='FTX Yedek', width=12,font=('Arial',13,'bold')).grid(row=11,column=2)
coinbase_check=Checkbutton(exchange_button_frame,variable=coinbase, onvalue='coinbase', offvalue='', text='Coinbase', width=12,font=('Arial',13,'bold')).grid(row=12,column=0)
kraken_check=Checkbutton(exchange_button_frame,variable=kraken, onvalue='kraken', offvalue='', text='Kraken', width=12,font=('Arial',13,'bold')).grid(row=12,column=1)
bitfinex_check=Checkbutton(exchange_button_frame,variable=bitfinex, onvalue='bitfinex', offvalue='', text='Bitfinex', width=12,font=('Arial',13,'bold')).grid(row=12,column=2)






title= Label(time_frame, text='Zaman aralığı', font=('Arial',18,'bold'), fg='red', ).grid(row=14,column=0,sticky='w', pady=(15,0), padx=(10,0))

time_label_1= Label(time_label_frame, text='YYYY/AA/GG/SS/DD<=', font=('Arial',10,'bold'), fg='red', ).grid(row=15,column=0,sticky='w', pady=(15,0), padx=(15,45))
from_year=Entry(time_label_frame,width= 20)
from_year.insert(0,'Örn 2022/05/19/21/59')
from_year.bind("<Button-1>", reset_from)
from_year.place(relx= .05, rely= .75, anchor= CENTER,)

time_label_2= Label(time_label_frame, text='=>YYYY/AA/GG/SS/DD', font=('Arial',10,'bold'), fg='red', ).grid(row=15,column=1,sticky='w', pady=(15,0), padx=(45,0))
to_year=Entry(time_label_frame,width= 20)
to_year.insert(0,'Örn 2022/06/01/15/37')
to_year.bind("<Button-1>", reset_to)
to_year.place(relx= .18, rely= .75, anchor= CENTER,)


#Error label
error_label=Label(error_frame, text='',font=('Arial',12,'bold'), fg='red',padx=10, pady=20 )
error_label.grid(row=0,column=0)

#Button to get the tables
balance=Button(button_frame, text='Get Balance',width=11,height=2, bg='#23BA86', font=('Arial', 15, 'bold'), command=fetch_balance).grid(row=20, column=0, pady=(35,45),padx=20)
excel=Button(button_frame, text='Get Excel',width=11,height=2, bg='#0D8DDE', font=('Arial', 15, 'bold'), command=fetch_excel).grid(row=20, column=1, pady=(35,45),padx=20)

#show_livesrates()

root.mainloop()



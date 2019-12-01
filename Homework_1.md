# Homework 1
## Wang Bingquan
## 1801212932
# Use tick data of stocks to mining technical factor for guiding stocks trading within a day
## 1. Introduction
This topic want to use genetic programming method to mining technical factors based on the tick data of stocks. The tick data contains 
all the transactions happening in one period. Shanghai Stock Exchange and Shenzhen Stock Exchange would refresh the tick data each 
millisecond, however, we do not need factors in this frequency because of the limit of calculation speed. The transactions happened 
in each second will be aggregated to create a snapshot including some basic quota information: highest-price, lowest-price, open-price, 
close-price, volume, amount and return. There are over 3800 stocks in China A share market and the size of quota in one day is over 2 GB. 
What's more, the news data in financial websites or applications such as Snowball and East-money will be collected by scraping and used to 
analyze the the market sentiment of single stock. It is also a factor to analyze the price trend and will be refreshed in second frequency 
same as factors based in quota factor. All the data used to create factors is quite huge and hard for computer to process in a short time. 
Therefore, this topic is accordance with the volume characteristics of big data projects.  
Because all the data will be refreshed in each millisecond and the snapshot is created in each second, the factors based on this data 
can be used to predict the price trends of all the stocks quickly. For example, it will predict the price change of all the stocks in 
future 5 seconds and buy stocks with highest probability of price rising, sell stocks with highest probability of price slide. 
The velocity in big data characteristics means that the data movement is now almost real time and the update window has reduced to 
fractions of the seconds. The speed of factors calculation and trading decision also meet this standard.  
The tick data provided by Shanghai Stock Exchange and Shenzhen Stock Exchange is stored in csv format. Beacuse input and output of 
hdf5 files are more fast in python, the tick data will be stored in hdf5 format. The news information 
could be saved in kinds format such as pdf or html. To make the news information easy to process, it will be stored in simple text 
format. The various kinds of data storage is accordance with variety characteristic of big data project.  
## 2.Workflow
Genetic programing method is used to generate formula calculating new factors based on the one-second frequency snapshot data list before.
In each day, the factors will be evaluated by IC or IR; those factors with lower predicting capability will be dropped and newly effective 
factors will be added. There may be over hundreds of technical factors and we need to calculate the probability of price change based on 
these factors in each second. To get better calculation efficiency, this system use linear regression to predict the price change. It use 
historical data in last 5 days to train model and refresh the parameters every hour during the trading period. In each second, the model 
could use the factors to predict the price change in future 5 seconds and make transaction of stocks based on the probability of price 
change. The workflow is shown in the picture below.  
![Piciture 1 Workflow](https://github.com/WangBingquan96/BigData-Homework/blob/master/workflow.png)
## 3.Data storage
The tick data and news information is time series data. Because the speed of data collection, storage and calculation is significant 
in this system, it uses InfluxDB to store the data to get higher I/O efficiency. InfluxDB is an open-source time series database (TSDB) 
developed by InfluxData. It is written in Go and optimized for fast, high-availability storage and retrieval of time series data in 
fields such as operations monitoring, application metrics, Internet of Things sensor data, and real-time analytics. It can quickly 
collect and store the tick data provided by exchange; it will also quickly output the data for refreshing the factors value in each second.









//+------------------------------------------------------------------+
//|                                               Robot KC + MGD.mq5 |
//|                                                 Darwint-Maksimov |
//|                                           https://www.darwint.ru |
//+------------------------------------------------------------------+
#property copyright "Darwint-Maksimov"
#property link      "https://www.darwint.ru"
#define VERSION "2.06"
#property version   VERSION

//+------------------------------------------------------------------+
//| Include                                                          |
//+------------------------------------------------------------------+
#include "Include\Expert.mqh"
#include "Include\EnumTypes.mqh"

#include "Include\SignalKC + EMA.mqh"
#include "Include\MoneyManage.mqh"
#include "Include\TrailingKeltnerChannel.mqh"
//+------------------------------------------------------------------+
//| Enums                                                            |
//+------------------------------------------------------------------+
/*enum ENUM_KELTNER_SIGNAL_LINE//определение сигнальной линии
{
   USE_OUTER = 1,
   USE_CENTER = 2
};*/
//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
//--- inputs for expert
input string Expert_Title                        ="Robot KC + EMA";  // Document name
ulong        Expert_MagicNumber                  =19389; //
bool         Expert_EveryTick                    =false; //
//--- inputs for main signal
int          Signal_ThresholdOpen                =100;   // Signal threshold value to open [0...100]
int          Signal_ThresholdClose               =100;   // Signal threshold value to close [0...100]
double       Signal_PriceLevel                   =0.0;   // Price level to execute a deal
double       Signal_StopLevel                    =50.0;  // Stop Loss level (in points)
double       Signal_TakeLevel                    =50.0;  // Take Profit level (in points)
int          Signal_Expiration                   =10;

//--- inputs for indicators

input group "Outer Keltner Channel params"
input bool                 Signal_UseTrend                      = true;               //Проверять тренд по положению МГД и центральной линии канала
input int	               Signal_KeltnerChannelPeriod	       = 12;                 //Период
input	ENUM_MA_METHOD       Signal_KeltnerChannelMAMethod        = MODE_EMA;           //Метод усреднения
input ENUM_APPLIED_PRICE   Signal_KeltnerChannelPriceType	    = PRICE_TYPICAL;      //Тип цены
input	double               Signal_KeltnerChannelPriceMultIn     = 2;                  //Мультипликатор внутреннего канала
//input color                Signal_KeltnerChannelColorIn         = clrLimeGreen;       //
input	double               Signal_KeltnerChannelPriceMultOut	 = 4;                  //Мультипликатор внешнего канала
//input color                Signal_KeltnerChannelColorOut        = clrLightBlue;       //

input group    "EMA params"
input bool                 Signal_UseEMA                        = true;               //Использовать фильтр EMA
input int                  Signal_EMAPeriod                     = 14;                 //EMA: Период усреднения
input ENUM_APPLIED_PRICE   Signal_EMAPriceType                  = PRICE_TYPICAL;      //EMA: Тип цены

input group    "Common params"
input ulong                Expert_RobotID                       = 19389;
input bool                 Expert_Debug                         = true;               //Выводить сообщения для отладки 
input string               Expert_MonitorAddr                   = "http://192.168.0.129/receive/";     // Веб-адрес системы мониторинга

input group    "Order params"
input ENUM_KELTNER_SIGNAL_LINE  Signal_MethodIn                 = USE_OUTER;               //Открывать позицию на границе внутреннего канала (false = использовать центральную линию)
input ENUM_KELTNER_SIGNAL_LINE  Signal_MethodOut                = USE_OUTER;               //Закрывать позицию на границе внутреннего канала (false = использовать центральную линию)

//--- inputs for money
input group    "Money manage params"
input double               Money_MarginTest                     = 0.0;                //Money manage: ГО для тестирования склейки на истории. (0 - не учитывается)
input double               Money_FixRiskPercent                 = 5.0;                //Risk percentage, %
input double               Money_DepositePercentMax             = 50.0;               //Процент от депозита, %

input group    "Trailing params"
input bool               TrailingUseAdvancedTrailing          = false;               //Использовать усовершенствованную систему трейлинга
//+------------------------------------------------------------------+
//| Global expert object                                             |
//+------------------------------------------------------------------+
CExpert ExtExpert;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   string param_str = "";
   param_str += "Expert_Title=" + Expert_Title + "\n";
   
   param_str += "Signal_UseTrend=" + IntegerToString(Signal_UseTrend) + "\n";
   param_str += "Signal_KeltnerChannelPeriod=" + IntegerToString(Signal_KeltnerChannelPeriod) + "\n";
   param_str += "Signal_KeltnerChannelMAMethod=" + IntegerToString(Signal_KeltnerChannelMAMethod) + "\n";
   param_str += "Signal_KeltnerChannelPriceType=" + EnumToString(Signal_KeltnerChannelPriceType) + "\n";
   param_str += "Signal_KeltnerChannelPriceMultIn=" + DoubleToString(Signal_KeltnerChannelPriceMultIn) + "\n";
   param_str += "Signal_KeltnerChannelPriceMultOut=" + DoubleToString(Signal_KeltnerChannelPriceMultOut) + "\n";


   param_str += "Signal_UseEMA=" + IntegerToString(Signal_UseEMA) + "\n";
   param_str += "Signal_EMAPeriod=" + IntegerToString(Signal_EMAPeriod) + "\n";
   param_str += "Signal_EMAPriceType=" + EnumToString(Signal_EMAPriceType) + "\n";

   param_str += "Expert_RobotID=" + IntegerToString(Expert_RobotID) + "\n";
   param_str += "Expert_Debug=" + IntegerToString(Expert_Debug) + "\n";
   param_str += "Expert_MonitorAddr=" + Expert_MonitorAddr + "\n";
   
   param_str += "Signal_MethodIn=" + EnumToString(Signal_MethodIn) + "\n";
   param_str += "Signal_MethodOut=" + EnumToString(Signal_MethodOut) + "\n";
   

   param_str += "Money_MarginTest=" + IntegerToString( Money_MarginTest) + "\n";
   param_str += "Money_FixRiskPercent=" + IntegerToString(Money_FixRiskPercent) + "\n";
   param_str += "Money_DepositePercentMax=" + IntegerToString(Money_DepositePercentMax) + "\n";
   
   param_str += "TrailingUseAdvancedTrailing=" + IntegerToString(TrailingUseAdvancedTrailing) + "\n";
   
   Print(param_str);
   
   Expert_MagicNumber = Expert_RobotID;
   
//--- Initializing expert
   if(!ExtExpert.Init(Symbol(),Period(),Expert_EveryTick,Expert_MagicNumber))
     {
      //--- failed
      printf(__FUNCTION__+": error initializing expert");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//--- Creating signal
   CExpertSignal *signal=new CExpertSignal;
   if(signal==NULL)
     {
      //--- failed
      printf(__FUNCTION__+": error creating signal");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//---
   ExtExpert.InitSignal(signal);
   signal.ThresholdOpen(Signal_ThresholdOpen);
   signal.ThresholdClose(Signal_ThresholdClose);
   signal.PriceLevel(Signal_PriceLevel);
   signal.StopLevel(Signal_StopLevel);
   signal.TakeLevel(Signal_TakeLevel);
   signal.Expiration(Signal_Expiration);
//--- Creating filter CSignalMGDCross
   CKeltnerSignal *filter0=new CKeltnerSignal;
   if(filter0==NULL)
     {
      //--- failed
      printf(__FUNCTION__+": error creating filter0");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
   signal.AddFilter(filter0);
//--- Set filter parameters
   filter0.UseEMA(Signal_UseTrend);
   filter0.KeltnerChannelPeriod(Signal_KeltnerChannelPeriod);
   filter0.KeltnerChannelMAMethod(Signal_KeltnerChannelMAMethod);
   filter0.KeltnerChannelPriceType(Signal_KeltnerChannelPriceType);
   filter0.KeltnerChannelPriceMultIn(Signal_KeltnerChannelPriceMultIn);
   filter0.KeltnerChannelPriceMultOut(Signal_KeltnerChannelPriceMultOut);
   filter0.UseTrend(Signal_UseTrend);
   filter0.UseEMA(Signal_UseEMA);
   filter0.EMAPeriod(Signal_EMAPeriod);
   filter0.EMAPriceType(Signal_EMAPriceType);
   filter0.RobotID(Expert_RobotID);
   filter0.MethodIn(Signal_MethodIn);
   filter0.Debug(Expert_Debug);
   
   signal.General(0); 
   
CTrailingKeltnerChannel *trailing=new CTrailingKeltnerChannel;
   if(trailing==NULL)
     {
      //--- failed
      printf(__FUNCTION__+": error creating trailing");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//--- Add trailing to expert (will be deleted automatically))
   if(!ExtExpert.InitTrailing(trailing))
     {
      //--- failed
      printf(__FUNCTION__+": error initializing trailing");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }  
   
//--- Set trailing parameters
   trailing.UseAdvancedTrailing(TrailingUseAdvancedTrailing);
   trailing.MethodOut(Signal_MethodOut);
   trailing.KeltnerChannelPeriod(Signal_KeltnerChannelPeriod);
   trailing.KeltnerChannelMAMethod(Signal_KeltnerChannelMAMethod);
   trailing.KeltnerChannelPriceType(Signal_KeltnerChannelPriceType);
   trailing.KeltnerChannelPriceMult(Signal_KeltnerChannelPriceMultIn);
   
//--- Creation of money object
   CMoneyManage *money=new CMoneyManage;
   if(money==NULL)
     {
      //--- failed
      printf(__FUNCTION__+": error creating money");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//--- Add money to expert (will be deleted automatically))
   if(!ExtExpert.InitMoney(money))
     {
      //--- failed
      printf(__FUNCTION__+": error initializing money");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//--- Set money parameters
   money.RiskPercent(Money_FixRiskPercent);
   money.DepositPercent(Money_DepositePercentMax);
   money.MarginTest(Money_MarginTest);
//--- Check all trading objects parameters
   if(!ExtExpert.ValidationSettings())
     {
      //--- failed
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
//--- Tuning of all necessary indicators
   if(!ExtExpert.InitIndicators())
     {
      //--- failed
      printf(__FUNCTION__+": error initializing indicators");
      ExtExpert.Deinit();
      return(INIT_FAILED);
     }
    
    
   if(!ExtExpert.InitRobotMonitor(Expert_Title,VERSION , 100, Expert_MonitorAddr, param_str)){
      printf(__FUNCTION__+": error initializing robot_monitor object");
      ExtExpert.Deinit();
      return(INIT_FAILED);
   }
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
      ExtExpert.Deinit();
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
      ExtExpert.OnTick();
  }
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
void OnTrade()
  {
//---
   ExtExpert.OnTrade();
  }
//+------------------------------------------------------------------+

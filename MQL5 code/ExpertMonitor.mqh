//+------------------------------------------------------------------+
//|                                                 RobotMonitor.mqh |
//|                                                 Darwint-Maksimov |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Darwint-Maksimov"
#property link      "https://www.mql5.com"

#property version   "3.01"


#include <MyInclude\json.mqh>


const string M_HTTP_METHOD = "POST";
const string M_HTTP_HEADERS = "Content-Type:application/x-www-form-urlencoded\nUser-Agent:Mozilla\nAccept:*/*";

class CRobotMonitor
  {
private:

   //--- input & init parameters
   string            m_Params;            // string contents of ParamFile
   ulong             m_Magic;             // expert magic number
   string            m_Symbol;            // symbol name
   long              m_Account;           // account number
   ENUM_TIMEFRAMES   m_Period;            // work timeframe
   string            m_Name;              // robot name
   string            m_Version;
   int               m_Timeout;           // timeout for WebRequest^ determines how much we wait for a responce
   string            m_RobotMonitorAddr;  // parameter-set value of robot monitor message receiver web addres
   
   //---local values
   double            m_position_volume;   // volume of position, 0 if closed, does not account for type of position
   datetime          m_status_timestamp;  // time of sending the status update
   string            m_str_period;        // string representation of timeframe
   int               m_trading_enabled;   // bit mask representing three levels of enabled autotrade
   int               m_limit_orders;      // number of limit orders by this robot
   bool              m_init_sent;         // boolean flag to indicate that init signal has been received by server
   CJAVal            m_init_msg;          // json variable, containing all the information of init message
   

public:
                     CRobotMonitor();
                    ~CRobotMonitor();
                    bool Init(ulong magic, string name, string robot_version, int timeout, string monitor_addr, string params);
                    void Deinit();
                    bool SendStatus();
                    bool SendRequest(CJAVal& body);
                    bool SendSignal(bool signal_on);
                    bool CheckInitMessage()     {return m_init_sent;}
                    
  };
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
CRobotMonitor::CRobotMonitor(void):m_Magic(0),
                                 m_Period(0),
                                 m_Account(0),
                                 m_Symbol(""),
                                 m_Name(""),
                                 m_Timeout(100),
                                 m_RobotMonitorAddr(""),
                                 m_init_sent(false)
{
   m_status_timestamp = TimeCurrent();
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
CRobotMonitor::~CRobotMonitor()
  {
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+  
bool CRobotMonitor::Init(ulong magic, string name, string robot_version, int timeout, string monitor_addr, string params){
   

   if (timeout != 0){
      m_Timeout = timeout;
   }
   
   if (magic == EMPTY_VALUE){
      Print("M",m_Magic, " ",__FUNCTION__,"Error: robot_id cannot be empty!");
      return false;
   } else {
      m_Magic = magic;
   }
   
   Print("M",m_Magic, " ",__FUNCTION__,":---------------------");
   
   if (name == ""){
      Print("M",m_Magic, " ",__FUNCTION__,"Error: robot name cannot be empty!");
      return false;
   } else{
      m_Name = name;
   }
   
   if (monitor_addr == ""){
      Print("M",m_Magic," RobotMonitor turned off!");
      return true; // Монитор не нужен
   } else {
      m_RobotMonitorAddr = monitor_addr;
   }
   
   if (params == ""){
      Print (m_Magic," ",__FUNCTION__," Error: empty parameter string!");
      return false;
   } else {
      m_Params = params;
   }
   
   m_Symbol = Symbol();
   
   m_Account = AccountInfoInteger(ACCOUNT_LOGIN);   
   m_Period = _Period;
   m_str_period = StringSubstr(EnumToString(m_Period), 7, -1);       // получаем строковое представление таймфрейма, обрезая "PERIOD_" в начале строки
   m_Version = robot_version;
   
   m_init_sent = false;
   
   if (SendSignal(true)){
      Print("M",m_Magic, " ",__FUNCTION__,": sent signal on to server");
   } else {
      return false;
   }
   
   return true;
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void CRobotMonitor::Deinit(void){
   if (SendSignal(false)) {
      Print("M",m_Magic," ",__FUNCTION__,": sent signal off to server");
   }
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CRobotMonitor::SendStatus(void){
//--- Making sure we have relevant values
   // Проверяем, нужно ли запускать робот
   if (m_RobotMonitorAddr == "") return true;
   
   
   //проверяем, прошло ли достаточно времени после отправки последнего сообщения
   datetime now = TimeCurrent();
   if (m_status_timestamp + 30 > now ) return true;
   
   Print("M",m_Magic," ",__FUNCTION__,":---------------------");
   if (!m_init_sent){
      Print("M",m_Magic," ",__FUNCTION__,": Re-sending init msg");
       if (SendRequest(m_init_msg)){
         m_init_sent = true;
       }
   }
   if (!m_init_sent){
      Print("M",m_Magic," ",__FUNCTION__,": Init message not sent. Aborting status sending.");
      return false;
   }

   //--- update volume
   m_position_volume = 0.0;
   if (PositionSelect(m_Symbol)){
      if (PositionGetInteger(POSITION_MAGIC) == m_Magic){
         m_position_volume = PositionGetDouble(POSITION_VOLUME);   
         if (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
            m_position_volume *= -1;
      }
      
   } 
   
   m_status_timestamp = now;
   
   //--- update permissions
   m_trading_enabled = 0;
   if (TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)==1) {
      m_trading_enabled += 1;
   }      
   if (MQLInfoInteger(MQL_TRADE_ALLOWED) == 1) {
      m_trading_enabled += 2;
   }
   if ( AccountInfoInteger(ACCOUNT_TRADE_EXPERT) == 1){
      m_trading_enabled += 4;
   }
   if ( AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) == 1){
      m_trading_enabled += 8;
   }
   
   m_limit_orders = OrdersTotal();
   
//--- Creating json format for status update

   CJAVal   m_json_body;  // json form of request body
   
   m_json_body["robot_id"]          = m_Magic;
   m_json_body["robot_name"]        = m_Name;
   m_json_body["datetime"]          = TimeToString(m_status_timestamp);
   m_json_body["robot_volume"]      = m_position_volume;
   m_json_body["robot_trading_enabled"] = m_trading_enabled;
   m_json_body["robot_limit_orders"] = m_limit_orders;
   m_json_body["robot_symbol"]      = m_Symbol;
   m_json_body["robot_timeframe"]   = m_str_period;
   m_json_body["robot_account_code"] = m_Account;
   
//--- Sending request to RobotMonitor
   ResetLastError();
   if (!SendRequest(m_json_body)){
      Print("M",m_Magic," ",__FUNCTION__,": result: ", false);
      return false;
   }
   
   Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
   return true;
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CRobotMonitor::SendRequest(CJAVal &body){

//--- Declaring and converting variables
   string      m_request_string;                   // string representation, required for conversion from json to char[]
   char        m_request_body[];                   // char[], required by WebRequest()
   char        m_response_body[];
   string      m_response_headers;
   
   
   
   body.Serialize(m_request_string);
   Print("M",m_Magic," ",__FUNCTION__,": ",m_request_string);
   StringToCharArray(m_request_string, m_request_body);
   
   ResetLastError();
   int m_web_result = WebRequest(
                                 M_HTTP_METHOD,
                                 m_RobotMonitorAddr,
                                 M_HTTP_HEADERS,
                                 m_Timeout,
                                 m_request_body,
                                 m_response_body,
                                 m_response_headers
                                 );

   //Print("RobotMonitor web request returned ", CharArrayToString(m_response_body));
   if (m_web_result == -1){
      Print("M",m_Magic," ",__FUNCTION__,": result: ",false);
      Print("M",m_Magic," ",__FUNCTION__,": Error ",GetLastError());
      return false;
   }
   
   if (CharArrayToString(m_response_body) != "Ok"){
      Print("M",m_Magic," ",__FUNCTION__,": result: ",false);
      Print("M",m_Magic," ",__FUNCTION__,": Error!! Server returned : ",m_web_result," with msg: ",CharArrayToString(m_response_body));
      return false;
   }
   
   Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
   Print("M",m_Magic," ",__FUNCTION__,": Server returned : ",m_web_result," with msg: ",CharArrayToString(m_response_body));
   
   return true;   
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CRobotMonitor::SendSignal(bool signal_on)
{
   //Проверяем, нужно ли запускать мониторинг
   
   if (m_RobotMonitorAddr == "") return true;
   Print("M",m_Magic," ",__FUNCTION__,":---------------------");
   string signal = (signal_on ? "on" : "off");
   
   //--- update permissions
   m_trading_enabled = 0;
   if (TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)==1) {
      m_trading_enabled += 1;
   }      
   if (MQLInfoInteger(MQL_TRADE_ALLOWED) == 1) {
      m_trading_enabled += 2;
   }
   if ( AccountInfoInteger(ACCOUNT_TRADE_EXPERT) == 1){
      m_trading_enabled += 4;
   }
   if ( AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) == 1){
      m_trading_enabled += 8;
   }
   
   m_status_timestamp = TimeCurrent();
   
//--- Creating json format for status update

   CJAVal   m_json_body;                   // json form of request body
   
   m_json_body["robot_id"]          = m_Magic;
   m_json_body["robot_signal"]      = signal;
   m_json_body["datetime"]          = TimeToString(m_status_timestamp);
   m_json_body["robot_name"]        = m_Name;
   m_json_body["robot_symbol"]      = m_Symbol;
   m_json_body["robot_timeframe"]   = m_str_period;
   m_json_body["robot_params"]      = m_Params;
   m_json_body["robot_trading_enabled"] = m_trading_enabled;
   m_json_body["robot_account_code"] = m_Account;
   m_json_body["robot_version"] = m_Version;
   
   ResetLastError();
   if (!SendRequest(m_json_body)){
      m_init_msg = m_json_body;
      m_init_sent = false;
      return true;
   }else {
      m_init_sent = true;
   }
   Print("M",m_Magic," ",__FUNCTION__,": result: ",m_init_sent);
   return true;

}
//+------------------------------------------------------------------+

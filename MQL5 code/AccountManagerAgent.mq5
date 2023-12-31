//+------------------------------------------------------------------+
//|                                          AccountManagerAgent.mq5 |
//|                                                 Darwint-Maksimov |
//|                                           https://www.darwint.ru |
//+------------------------------------------------------------------+
#property copyright "Darwint-Maksimov"
#property link      "https://www.darwint.ru"
#property version   "1.05"
#property service

#include <MyInclude\json.mqh>
#include <Trade\AccountInfo.mqh>
//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+

input string   ManagerAddress  = "http://192.168.0.20/receive/"; // адрес системы управления счетами
input bool     DEBUG    = false;        // Включить режим отладки
input bool     Send_Full_History    = false;        // Отправлять всю историю
//+------------------------------------------------------------------+
//| Constants                                                        |
//+------------------------------------------------------------------+
const string M_HTTP_METHOD = "POST";
const string M_HTTP_HEADERS = "Content-Type:application/x-www-form-urlencoded\nUser-Agent:Mozilla\nAccept:*/*";
const string m_Magic = "AccountManager Agent";
const string g_History = "AM_Agent_Accounted_History";
//+------------------------------------------------------------------+
//| Variables                                                       |
//+------------------------------------------------------------------+
long           m_Account;           // account number
CAccountInfo   AccountInfo;  // accountinfo for login_check
int            m_Timeout = 1000;      // request timeout, mlsec
bool           m_SendHistory = false;
int            m_MinuteTicks = 0;
CJAVal         m_SavedPositions;
//+------------------------------------------------------------------+
//| Service program start function                                   |
//+------------------------------------------------------------------+
void OnStart()
  {
//---
   Print("############ AccountManagerAgent started ############");
   string input_param_str = "";
   input_param_str += "ManagerAddress="+ (string)ManagerAddress + "\n";
   input_param_str += "DEBUG="+ (string)DEBUG + "\n";
   Print(input_param_str);
   
   if (AccountInfo.Login() <= 0) {
      Print("Account login not set. Exit with error.");
      return;
   }
   
   m_Account = AccountInfoInteger(ACCOUNT_LOGIN);
   m_SendHistory = Send_Full_History;
   
   if (!SendHistory()){
      Print("Could not send account history! Exit with error.");
      return;
   }
   
   while(!IsStopped()){
      //sleep(3600000); // ожидать 1 час
      Main();
      Sleep(60000); // 60 seconds
   }
   
  }
//+------------------------------------------------------------------+
//| OnStart sending trading history                                  |
//+------------------------------------------------------------------+
bool SendHistory(){

   datetime dt_now = TimeCurrent();
   datetime dt_start;
   


   if (!GlobalVariableCheck(g_History) || m_SendHistory){ // если существует записанная дата, то мы можем отправлять только последние данные, а не все
      dt_start = 0;
   } else {
      dt_start = (datetime)GlobalVariableGet(g_History);
   }
   
   HistorySelect(dt_start, dt_now);
   
   
   //обработка ордеров
   int history_orders = HistoryOrdersTotal();
   if (history_orders == 0){
      Print("M",m_Magic," ",__FUNCTION__,": No available history!");
      return true;
   } else {
      Print("M",m_Magic," ",__FUNCTION__,": Has ",history_orders," orders!");
   }
   CJAVal json_orders_array;
   
   for (int i = 0; i < history_orders; i++){
      CJAVal json_orders_elem;
      
      ulong ticket = HistoryOrderGetTicket(i);
      
      
      if (ticket > 0){ //если ордер успешно скопирован в кэш, работаем с ним
         
         json_orders_elem["ticket"] = ticket;
         
         json_orders_elem["setup_time"] = TimeToString((datetime)HistoryOrderGetInteger(ticket, ORDER_TIME_SETUP));
         json_orders_elem["type"] = HistoryOrderGetInteger(ticket, ORDER_TYPE);
         json_orders_elem["state"] = HistoryOrderGetInteger(ticket, ORDER_STATE);
         json_orders_elem["expiration_time"] = TimeToString((datetime)HistoryOrderGetInteger(ticket, ORDER_TIME_EXPIRATION));
         json_orders_elem["done_time"] = TimeToString((datetime)HistoryOrderGetInteger(ticket, ORDER_TIME_DONE));
         json_orders_elem["setup_msc_time"] = HistoryOrderGetInteger(ticket, ORDER_TIME_SETUP_MSC);
         json_orders_elem["done_msc_time"] = HistoryOrderGetInteger(ticket, ORDER_TIME_DONE_MSC);
         json_orders_elem["filling_type"] = HistoryOrderGetInteger(ticket, ORDER_TYPE_FILLING);
         json_orders_elem["time_type"] = HistoryOrderGetInteger(ticket, ORDER_TYPE_TIME);
         json_orders_elem["magic"] = HistoryOrderGetInteger(ticket, ORDER_MAGIC);
         json_orders_elem["reason"] = HistoryOrderGetInteger(ticket, ORDER_REASON);
         json_orders_elem["position_id"] = HistoryOrderGetInteger(ticket, ORDER_POSITION_ID);
         json_orders_elem["close_by_position_id"] = HistoryOrderGetInteger(ticket, ORDER_POSITION_BY_ID);
         
         json_orders_elem["volume_initial"] = HistoryOrderGetDouble(ticket, ORDER_VOLUME_INITIAL);
         json_orders_elem["volume_current"] = HistoryOrderGetDouble(ticket, ORDER_VOLUME_CURRENT);
         json_orders_elem["price_open"] = HistoryOrderGetDouble(ticket, ORDER_PRICE_OPEN);
         json_orders_elem["sl"] = HistoryOrderGetDouble(ticket, ORDER_SL);
         json_orders_elem["tp"] = HistoryOrderGetDouble(ticket, ORDER_TP);
         json_orders_elem["price_current"] = HistoryOrderGetDouble(ticket, ORDER_PRICE_CURRENT);
         json_orders_elem["price_stoplimit"] = HistoryOrderGetDouble(ticket, ORDER_PRICE_STOPLIMIT);
         
         json_orders_elem["symbol"] = HistoryOrderGetString(ticket, ORDER_SYMBOL);
         json_orders_elem["comment"] = HistoryOrderGetString(ticket, ORDER_COMMENT);
         json_orders_elem["external_id"] = HistoryOrderGetString(ticket, ORDER_EXTERNAL_ID);
         
         json_orders_array[i] = json_orders_elem;
         if (DEBUG) Print("M",m_Magic," ",__FUNCTION__,":order ", json_orders_elem.Serialize());
      }
   }
   //json_body["orders"] = json_orders_array;
   
   //обработка сделок
   int history_deals = HistoryDealsTotal();
   if (history_deals == 0){
      Print("M",m_Magic," ",__FUNCTION__,": No available history!");
      return true;
   } else {
      Print("M",m_Magic," ",__FUNCTION__,": Has ",history_deals," deals!");
   }
   CJAVal json_deals_array;
   
   for (int i = 0; i < history_deals; i++){
      CJAVal json_deals_elem;
      ulong ticket = HistoryDealGetTicket(i);
      
      if (ticket > 0){
         json_deals_elem["ticket"] = ticket;
         
         json_deals_elem["order_id"] = HistoryDealGetInteger(ticket, DEAL_ORDER);
         json_deals_elem["time"] = TimeToString((datetime)HistoryDealGetInteger(ticket, DEAL_TIME));
         json_deals_elem["time_msc"] = HistoryDealGetInteger(ticket, DEAL_TIME_MSC);
         json_deals_elem["type"] = HistoryDealGetInteger(ticket, DEAL_TYPE);
         json_deals_elem["entry"] = HistoryDealGetInteger(ticket, DEAL_ENTRY);
         json_deals_elem["magic"] = HistoryDealGetInteger(ticket, DEAL_MAGIC);
         json_deals_elem["reason"] = HistoryDealGetInteger(ticket, DEAL_REASON);
         json_deals_elem["position_id"] = HistoryDealGetInteger(ticket, DEAL_POSITION_ID);
         
         json_deals_elem["volume"] = HistoryDealGetDouble(ticket, DEAL_VOLUME);
         json_deals_elem["price"] = HistoryDealGetDouble(ticket, DEAL_PRICE);
         json_deals_elem["commission"] = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
         json_deals_elem["swap"] = HistoryDealGetDouble(ticket, DEAL_SWAP);
         json_deals_elem["profit"] = HistoryDealGetDouble(ticket, DEAL_PROFIT);
         json_deals_elem["fee"] = HistoryDealGetDouble(ticket, DEAL_FEE);
         
         json_deals_elem["symbol"] = HistoryDealGetString(ticket, DEAL_SYMBOL);
         json_deals_elem["comment"] = HistoryDealGetString(ticket, DEAL_COMMENT);
         json_deals_elem["external_id"] = HistoryDealGetString(ticket, DEAL_EXTERNAL_ID);
         
         json_deals_array[i] = json_deals_elem;
         if (DEBUG) Print("M",m_Magic," ",__FUNCTION__,":deal ", json_deals_elem.Serialize());
      }
   }
   
   CJAVal   json_body;  // json form of request body
   json_body["account"]           = m_Account;
   json_body["timestamp"]         = TimeToString(TimeCurrent());
   json_body["rewrite_history"]   = m_SendHistory;
   
   if (history_deals <= 1500){
      json_body["orders"] = json_orders_array;
      json_body["deals"] = json_deals_array;
      ResetLastError();
      if (!SendRequest(json_body)){
         Print("M",m_Magic," ",__FUNCTION__,": result: ", false);
         return false;
      }
      
      m_SendHistory = false;
      Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
      GlobalVariableSet(g_History,(double)dt_now);
      return true;
   }

   int batches = (history_deals / 1500) + 1;
   
   int deal_batch = history_deals/batches + 1;
   int order_batch = history_orders/batches + 1;
   
   for(int i = 0; i < batches; i++){
      int deal_start = deal_batch * i;
      int order_start = order_batch * i;
      
      CJAVal msg = json_body;
      msg["rewrite_history"] = m_SendHistory;
      CJAVal msg_deals;
      for(int d = 0; d < deal_batch && d+deal_start < history_deals; d++){
         msg_deals[d] = json_deals_array[deal_start + d];
      }
      msg["deals"] = msg_deals;
      
      CJAVal msg_orders;
      for(int d = 0; d < order_batch && d+order_start < history_orders; d++){
         msg_orders[d] = json_orders_array[order_start + d];
      }
      msg["orders"] = msg_orders;
      
      ResetLastError();
      if (!SendRequest(msg)){
         Print("M",m_Magic," ",__FUNCTION__,": result: ", false);
         return false;
      }
      m_SendHistory = false;
   }
   
   Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
   GlobalVariableSet(g_History,(double)dt_now);
   return true;
   
}
//+------------------------------------------------------------------+
//| Main function for hourly message sending                         |
//+------------------------------------------------------------------+
void Main(){

   if (StateChanged() || (m_MinuteTicks % 5) == 0){
      SendMessage();
   }
   
   if ( m_MinuteTicks == 60){
      m_MinuteTicks = 0;
      SendHistory();
   }
   m_MinuteTicks ++;
   
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool StateChanged(){
   if (DEBUG) Print("M",m_Magic, " ",__FUNCTION__,":---------------------");
   bool result = false;

   int positions_count = PositionsTotal();
   if (m_SavedPositions.Size() != positions_count) result = true;
   
   for (int i = 0; i < positions_count; i++){
      string symbol = PositionGetSymbol(i);
      if(!m_SavedPositions.HasKey(symbol)) return true;
         
      if(m_SavedPositions[symbol].HasKey("id") &&                                      // json contains info about id
         m_SavedPositions[symbol]["id"] != PositionGetInteger(POSITION_IDENTIFIER) ||   // id differs between realtime data and saved data
         !m_SavedPositions[symbol].HasKey("id")) result = true;                          // json doesn"t contain id - possible error, requiers refreshing of data 
      
      if(m_SavedPositions[symbol].HasKey("price") &&                                      // json contains info about price
         m_SavedPositions[symbol]["price"] != PositionGetDouble(POSITION_PRICE_OPEN) ||   // price differs between realtime data and saved data
         !m_SavedPositions[symbol].HasKey("price")) result = true;                          // json doesn"t contain price - possible error, requiers refreshing of data 
         
      if(m_SavedPositions[symbol].HasKey("magic") &&                                // json contains info about magic
         m_SavedPositions[symbol]["magic"] != PositionGetInteger(POSITION_MAGIC) ||  // magic differs between realtime data and saved data
         !m_SavedPositions[symbol].HasKey("magic")) result = true;                    // json doesn"t contain magic - possible error, requiers refreshing of data 
         
      if(m_SavedPositions[symbol].HasKey("sl") &&                                   // json contains info about sl
         m_SavedPositions[symbol]["sl"] != PositionGetDouble(POSITION_SL) ||        // sl differs between realtime data and saved data
         !m_SavedPositions[symbol].HasKey("sl")) result = true;                       // json doesn"t contain sl - possible error, requiers refreshing of data 
         
      int volume_sign = -1 * (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL?1:-1); // modify volume for negative volumes for short positions
      if(m_SavedPositions[symbol].HasKey("volume") &&                                  // json contains info about volume
         m_SavedPositions[symbol]["volume"] != PositionGetDouble(POSITION_VOLUME)*volume_sign ||   // volume differs between realtime data and saved data
         !m_SavedPositions[symbol].HasKey("volume")) result = true;                      // json doesn"t contain volume - possible error, requiers refreshing of data 
   }
   
   if (DEBUG) Print("M",m_Magic," ",__FUNCTION__,": result: ", result);
   
   return result;
}
//+------------------------------------------------------------------+
//| loop sending message                                             |
//+------------------------------------------------------------------+
bool SendMessage(){

   Print("M",m_Magic, " ",__FUNCTION__,":---------------------");
   
   CJAVal   json_body;  // json form of request body
   m_SavedPositions = json_body; // обнуление переменной, чтобы закрывшиеся позиции дропнулись.
   
   json_body["account"]    = m_Account;
   json_body["timestamp"]  = TimeToString(TimeCurrent());
   json_body["balance"]    = AccountInfoDouble(ACCOUNT_BALANCE);
   json_body["sum_risk"]  = 0.0;
   
   CJAVal json_positions_array;
   
   int positions=PositionsTotal();
   //--- пробежим по списку позиций
   for(int i=0;i<positions;i++){
      ResetLastError();
      //--- скопируем в кэш позицию по ее номеру в списке
      string symbol=PositionGetSymbol(i); //  попутно получим имя символа, по которому открыта позиция
      if(symbol!=""){ // позицию скопировали в кэш, работаем с ней
         CJAVal next_position = CalculatePositionParams();
         json_body["sum_risk"] = json_body["sum_risk"].ToDbl() + next_position["risk"].ToDbl();
         json_positions_array[i] = next_position;
      }
      else {           // вызов PositionGetSymbol() завершился неудачно
         Print("M",m_Magic, " ",__FUNCTION__,":Ошибка при получении в кэш позиции c индексом ",i,". Код ошибки: ",GetLastError());
      }
   }
   
   if (json_positions_array.Size() != 0){
      string str;
      json_positions_array.Serialize(str);
      json_body["positions"] = str;
      Print("Positions_json",str, " Size of array=",json_positions_array.Size());
   } else
      json_body["positions"] = " ";

   
//--- Sending request to RobotMonitor
   ResetLastError();
   if (!SendRequest(json_body)){
      Print("M",m_Magic," ",__FUNCTION__,": result: ", false);
      return false;
   }
   
   Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
   return true;
}
//+------------------------------------------------------------------+
//| Calculating json form with actual parameters of a position       |
//+------------------------------------------------------------------+
CJAVal CalculatePositionParams(){
   CJAVal position_params;
   
   string symbol = PositionGetString(POSITION_SYMBOL);
   position_params["price"] = PositionGetDouble(POSITION_PRICE_OPEN);
   int volume_sign = -1 * (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_SELL?1:(-1)); // modify volume for negative volumes for short positions
   position_params["volume"] = PositionGetDouble(POSITION_VOLUME)*volume_sign;
   double position_sl = PositionGetDouble(POSITION_SL);
   position_params["sl"] = position_sl;
   position_params["id"] = PositionGetInteger(POSITION_IDENTIFIER);
   position_params["magic"] = PositionGetInteger(POSITION_MAGIC);
   
   m_SavedPositions[symbol] = position_params; // saving position
   position_params["symbol"] = symbol;
   
   ENUM_ORDER_TYPE ord_type = PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY?ORDER_TYPE_BUY:ORDER_TYPE_SELL;
   double risk;
   
   if(position_sl != 0)  risk = AccountInfo.OrderProfitCheck(symbol, ord_type, PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PRICE_OPEN), PositionGetDouble(POSITION_SL));
   else risk = AccountInfo.Balance();
   //position_params["risk"] = MathAbs(risk) / AccountInfo.Balance() * 100.0; //percent
   position_params["risk"] = MathAbs(risk) ; //money
   return position_params;
   
}
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool SendRequest(CJAVal &body){

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
                                 ManagerAddress,
                                 M_HTTP_HEADERS,
                                 m_Timeout,
                                 m_request_body,
                                 m_response_body,
                                 m_response_headers
                                 );

   //Print("RobotMonitor web request returned ", CharArrayToString(m_response_body));
   if (m_web_result == -1){
      Print("M",m_Magic," ",__FUNCTION__,": Error ",GetLastError());
      Print("M",m_Magic," ",__FUNCTION__,": result: ",false);
      return false;
   }
   
   if (CharArrayToString(m_response_body) != "Ok"){
      Print("M",m_Magic," ",__FUNCTION__,": Error!! Server returned : ",m_web_result," with msg: ",CharArrayToString(m_response_body));
      Print("M",m_Magic," ",__FUNCTION__,": result: ",false);
      return false;
   }
   
   Print("M",m_Magic," ",__FUNCTION__,": Server returned : ",m_web_result," with msg: ",CharArrayToString(m_response_body));
   Print("M",m_Magic," ",__FUNCTION__,": result: ",true);
   
   return true;   
}

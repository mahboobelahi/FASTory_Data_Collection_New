# FASTory-Data-Collection-New
Collects FASTory Line's Main Conveyor Belt Motor Driver Power Consumption Data for BT ranging 75-85 percent.
This data will be used by FASTory Energy Monitoring App during Initial development phase and testing. 
this the Power consumption data was collected for different work loads at 75-85% conveyor belt tension and stores in SQlit3 data base. This data retrives from DB and store in a CSV file for future use.
Data records will be reads from CSV file and sends to ZDMP DAQ after every one sec (In RT the Power consumption measurements were collected at 1sce sampling rate).


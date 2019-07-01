#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define MAX_TIME 85
#define DHT11PIN 7
#define ATTEMPTS 5                 //retry 5 times when no response
int dht11_val[5]={0,0,0,0,0};
char data[200];
void init(){
	wiringPiSetup();
}
char* dht11_read_val(){

    uint8_t lststate=HIGH;         //last state
    uint8_t counter=0;
    uint8_t j=0,i;
	int aa,bb;
	char data1[20],data2[20],text1[20]="{\"temp\":\"",text2[20]="\",\"humidity\":\"",text3[20]="\"}";
	char text[100]="false";
    for(i=0;i<5;i++)
        dht11_val[i]=0;

    //host send start signal    
    pinMode(DHT11PIN,OUTPUT);      //set pin to output 
    digitalWrite(DHT11PIN,LOW);    //set to low at least 18ms 
    delay(18);
    digitalWrite(DHT11PIN,HIGH);   //set to high 20-40us
    delayMicroseconds(40);

    //start recieve dht response
    pinMode(DHT11PIN,INPUT);       //set pin to input
    for(i=0;i<MAX_TIME;i++)         
    {
        counter=0;
        while(digitalRead(DHT11PIN)==lststate){     //read pin state to see if dht responsed. if dht always high for 255 + 1 times, break this while circle
            counter++;
            delayMicroseconds(1);
            if(counter==255)
                break;
        }
        lststate=digitalRead(DHT11PIN);    //read current state and store as last state. 
        if(counter==255)   //if dht always high for 255 + 1 times, break this for circle
            break;
 // top 3 transistions are ignored, maybe aim to wait for dht finish response signal
        if((i>=4)&&(i%2==0)){
            dht11_val[j/8]<<=1;     //write 1 bit to 0 by moving left (auto add 0)
            if(counter>16)      //long mean 1
                dht11_val[j/8]|=1;     //write 1 bit to 1 
            j++;
        }
    }
    // verify checksum and print the verified data
	
    if((j>=40)&&(dht11_val[4]==((dht11_val[0]+dht11_val[1]+dht11_val[2]+dht11_val[3])& 0xFF))){
		printf("--------------\n");
		printf("RH:%d,TEMP:%d\n",dht11_val[0],dht11_val[2]);
		aa=dht11_val[2];//获取湿度值
		bb=dht11_val[0];//获取温度值
		sprintf(data1,"%d",aa);//将湿度值由int转为char[]
		sprintf(data2,"%d",bb);//将温度值由int转为char[]
		strcpy(data,text1);//讲第一个字符数组复制到data数组中
		strcat(data,data1);//将剩下的数组包括温湿度的值的数组拼接起来
		strcat(data,text2);
		strcat(data,data2);
		strcat(data,text3);
		return data;

        
    }
    else{
		
		strcpy(data,text);
		return data;
        
	}
	
}

char* getData(){
	return data;
}
/*int main(void){
    int attempts=ATTEMPTS;
    if(wiringPiSetup()==-1)
        exit(1);
    while(1){                        //you have 5 times to retry
        int success = dht11_read_val();     //get result including printing out
        //if (success) {                      //if get result, quit program; if not, retry 5 times then quit
        //    break;
        //}
        //attempts--;
        delay(2500);
    }
    return 0;
}*/
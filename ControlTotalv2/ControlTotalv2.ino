#include "MPU9250.h"
//Sensor de inclinacion
MPU9250 mpu;
//Puertos inclinacion
int rpwm = 11;
int lpwm = 13;
//Puertos azimut
int mf = 8;
int pul = 10;
int dir = 12;
//Puertos radiacion
int pirhel = A0;
int pira = A1;
//Variables inclinacion
int anguloDeseado = 0;
int pitch = 0;
float incli = 0;
float acc = 0;
float mpupitch = 0;
//Variables azimut
int avance;
int enAzimut;
int dirAzimut;
int N = 30; //Relacion 30:1 del mecanismo
int P = 400; //Pulsos por revolucion
float brujulaX = 0;
float brujulaY = 0;
//Variables radiacion
float global = 0.0, directa = 0.0;
//Variable serial
String comSerial;
int nomore = 0;
String modo = "";
int c = 0;
int d = 0;
void setup() {
    Serial.begin(115200);
    Wire.begin();
    delay(2000);
    //Reducir frecuencia de muestreo
    if (!mpu.setup(0x68)) {  // change to your own address
        while (1) {
            Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
            delay(5000);
        }
    }

    //Pin inclinacion
    pinMode(13,OUTPUT);
    pinMode(11,OUTPUT);
    //Pin azimut
    pinMode(dir,OUTPUT);
    pinMode(pul,OUTPUT);
    pinMode(mf,OUTPUT);
}

void loop() {
  if(mpu.update()){ }
  /*if(modo == "Z"){
    if(mpu.update()){
      static uint32_t prev_ms = millis();
      if(millis() > prev_ms + 100){
        Serial.print(mpu.getMagX(),0);
        Serial.print(",");
        Serial.println(mpu.getMagY(),0);
        prev_ms = millis();
      }
    }
  }*/
  if(modo == "I"){
    if(mpu.update()){
      static uint32_t prev_ms2 = millis();
      if(millis() > prev_ms2 + 100){ 
        mpupitch = mpu.getPitch();//checar
        acc = mpu.getAccX();
        incli = (0.8*(mpupitch))+(0.2*(90*acc));
        pitch = incli + 90 + 7;
        prev_ms2 = millis();
      }
    }
    if(pitch > anguloDeseado){
      Serial.print(pitch);
      Serial.print(",");
      Serial.print("M"); //Imprime M de moviendose
      Serial.print(",");
      Serial.print("o");
      Serial.print(",");
      Serial.print("0.00");
      Serial.print(",");
      Serial.println("0.00");
      digitalWrite(13,LOW);   // turn the LED on (HIGH is the voltage level)
      digitalWrite(11,HIGH);// wait for a second
      delay(20);
      digitalWrite(11,LOW);
      delay(20);
    }
    else if(pitch < anguloDeseado){
      Serial.print(pitch);
      Serial.print(",");
      Serial.print("M"); //Imprime M de moviendose
      Serial.print(",");
      Serial.print("o");
      Serial.print(",");
      Serial.print("0.00");
      Serial.print(",");
      Serial.println("0.00");
      digitalWrite(11,LOW);   // turn the LED on (HIGH is the voltage level)
      digitalWrite(13,HIGH);// wait for a second
      delay(20);
      digitalWrite(13,LOW);
      delay(20);
    }
    else{
        digitalWrite(13,LOW);
        digitalWrite(11,LOW);
        delay(100);
        Serial.print(pitch);
        Serial.print(",");
        Serial.print("T");
        Serial.print(",");
        Serial.print("o");
        Serial.print(",");
        Serial.print("0.00");
        Serial.print(",");
        Serial.println("0.00");
    }
  }

  else if(modo == "R"){
    static uint32_t prev_ms3 = millis();
    if(millis() > prev_ms3 + 100){
    //Radiacion
      global = 5.0e3*(5.0*analogRead(pira)/1023.0)/11.0;
      directa = (5.0*analogRead(pirhel)/1023.0)*(1.0e6/392.41)/6.1;
      Serial.print("0");
      Serial.print(",");
      Serial.print("o");
      Serial.print(",");
      Serial.print("o");
      Serial.print(",");
      Serial.print(global);
      Serial.print(",");
      Serial.println(directa);
      prev_ms3 = millis();
    }
  }

  else if(modo == "M"){
    if(enAzimut == 1){
      digitalWrite(mf,LOW);
      if(dirAzimut == 0) digitalWrite(dir,HIGH);//Antihorario
      else digitalWrite(dir,LOW);//Horario
    //Ecuacion de pulsos (N*(azimut)*P/360);
      for(int x = 0; x <= avance; x++){
        digitalWrite(pul,HIGH);
        delay(5);
        digitalWrite(pul,LOW);
        delay(5);
        Serial.print("0");
        Serial.print(",");
        Serial.print("o");
        Serial.print(",");
        Serial.print("N");
        Serial.print(",");   
        Serial.print("0.00");
        Serial.print(",");
        Serial.println("0.00");
      }
      enAzimut = 0;
    }
    else{
      digitalWrite(mf,HIGH);
      digitalWrite(pul,LOW);
      delay(100);
      Serial.print("0");
      Serial.print(",");
      Serial.print("o");
      Serial.print(",");
      Serial.print("T");
      Serial.print(",");   
      Serial.print("0.00");
      Serial.print(",");  
      Serial.println("0.00");
    } 
  }

  //Comunicacion serial M,XXXX,Y,Z,II
  if(Serial.available()>0){
    comSerial = Serial.readString();
    //while(comSerial == 12)
    //M,XXX,Y,Z,W,H modo,pulsos,enAzimut,dirAzimut,enableInclinacion,dirInclinacion
    modo = comSerial.substring(0,1);
    avance = comSerial.substring(2,7).toInt();
    enAzimut = comSerial.substring(8,9).toInt();
    dirAzimut = comSerial.substring(10,11).toInt();
    anguloDeseado = comSerial.substring(12,14).toInt();
  }
}

#include <ArduinoJson.h>

const int pin1 = 6; // Aciona o pino 6 se o valor for 1
const int pin2 = 7; // Aciona o pino 7 se o valor for 2

void setup() {
  Serial.begin(9600);  // Inicializa a comunicação serial a 9600 bps
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    // Lê a linha da serial até '\n'
    String jsonString = Serial.readStringUntil('\n');
    jsonString.trim();
    
    if (jsonString.length() > 0) {
      Serial.print("Recebido JSON: ");
      Serial.println(jsonString);
      
      // Usando StaticJsonDocument para evitar avisos de depreciação
      StaticJsonDocument<200> doc;
      
      DeserializationError error = deserializeJson(doc, jsonString);
      if (error) {
        Serial.print("Falha ao desserializar JSON: ");
        Serial.println(error.f_str());
        return;
      }
      
      // Verifica se a chave "valor" existe verificando se não é nula
      if (!doc["valor"].isNull()) {
        int valor = doc["valor"];
        Serial.print("Valor recebido: ");
        Serial.println(valor);
        
        if (valor == 1) {
          digitalWrite(pin1, HIGH);
          digitalWrite(pin2, LOW);
        } else if (valor == 2) {
          digitalWrite(pin1, LOW);
          digitalWrite(pin2, HIGH);
        } else {
          // Para qualquer outro valor, desliga ambos os pinos
          digitalWrite(pin1, LOW);
          digitalWrite(pin2, LOW);
        }
      } else {
        Serial.println("Chave 'valor' não encontrada no JSON.");
      }
    }
  }
}

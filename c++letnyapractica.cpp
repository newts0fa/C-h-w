// Определяем пины по вашей схеме
const int ledPins[] = {4, 5, 6};
const int btnPins[] = {A0, A1, A2};
const int numElements = 3;

void setup() {
  Serial.begin(9600);
  
  for (int i = 0; i < numElements; i++) {
    pinMode(ledPins[i], OUTPUT);
    pinMode(btnPins[i], INPUT); // На схеме стоят внешние резисторы, используем обычный INPUT
  }
  
  randomSeed(analogRead(A5)); // Инициализация генератора случайных чисел
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "START") {
      runReactionGame();
    }
  }
}

void runReactionGame() {
  int attempts = random(3, 11); // Количество попыток от 3 до 10
  
  for (int i = 0; i < attempts; i++) {
    delay(random(1500, 4000)); // Случайное ожидание
    
    int activeIndex = random(0, numElements); // Выбираем случайный светодиод
    digitalWrite(ledPins[activeIndex], HIGH);
    
    long startTime = millis();
    bool pressed = false;
    
    while (!pressed) {
      for (int b = 0; b < numElements; b++) {
        // Проверяем нажатие. Если на схеме кнопки стянуты к GND, ловим HIGH.
        if (digitalRead(btnPins[b]) == HIGH) {
          long reactionTime = millis() - startTime;
          digitalWrite(ledPins[activeIndex], LOW);
          
          if (b == activeIndex) {
            Serial.print("RESULT:");
            Serial.println(reactionTime);
          } else {
            Serial.println("RESULT:WRONG_BTN");
          }
          
          pressed = true;
          delay(500); // Защита от дребезга
          break;
        }
      }
    }
  }
  Serial.println("FINISH");
}

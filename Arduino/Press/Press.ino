#include <Keyboard.h>

void setup() {
  Serial.begin(9600);  // Bắt đầu giao tiếp serial ở tốc độ 9600 bps
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();  // Đọc ký tự từ cổng Serial

    // Giả mạo ấn phím tương ứng với ký tự nhận được
    Keyboard.press(receivedChar);
    delay(10);  // Đợi 10ms
    Keyboard.releaseAll();  // Thả tất cả các phím
  }
}
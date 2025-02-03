const int outputPin = 2;  // D2 as output pin
const int inputPin = 3;   // D3 as input pin
int buttonState = 0;      // Store button state
int lastButtonState = LOW; // Store the last button state
unsigned long lastDebounceTime = 0;  // Last state change time
unsigned long debounceDelay = 50;    // Debounce delay

void setup() {
  Serial.begin(9600);     // Initialize serial communication, baud rate 9600
  pinMode(outputPin, OUTPUT);  // Set D2 as output
  pinMode(inputPin, INPUT);    // Set D3 as input
  digitalWrite(outputPin, HIGH);  // D2 outputs high level
}

void loop() {
  int reading = digitalRead(inputPin);  // Read the state of D3

  // If the state changes (from low to high or from high to low)
  if (reading != lastButtonState) {
    lastDebounceTime = millis();  // Record the state change time
  }

  // If the state remains stable for longer than the debounce delay
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // If the current state is different from the previously stored state
    if (reading != buttonState) {
      buttonState = reading;  // Update the button state
    }
  }

  lastButtonState = reading;  // Update the last button state

  // Real-time feedback of button state
  if (buttonState == HIGH) {
    Serial.println("-");  // Button is on, print "-"
  } else {
    Serial.println("+");   // Button is off, print "+"
  }

  delay(10);  // Appropriate delay to avoid too fast serial output
}
#include <LiquidCrystal.h>
#include <Bounce2.h>

#define RE(signal, state) (state=(state<<1)|(signal&1)&3)==1	// Macro para detectar rising edge

Bounce botao_1 = Bounce();	// Executa debounce no botão 1
const int botao_pin_1 = 10;	// Versão final teria 3 botões
const int motor_pin_1 = 11;	// Pino do motor (versão final teria 3 motores)
const int motor_duty_cycle = 50;	// Duty cycle em % dos motores
const int motor_delay = 2000;	// Delay de funcionamento do motor
int estado_botao = 0;
int item_selecionado = 0;


LiquidCrystal lcd(2, 3, 4, 5, 6, 7);
/* Cria objeto lcd da classe LiquidCrystal
 * RS     2
 * Enable 3
 * DB4    4
 * DB5    5
 * DB6    6
 * DB7    7
*/


void processar_compra(void) {
	// Selecionamos o motor a girar
	// de acordo com o valor de `item_selecionado`
	switch (item_selecionado) {
		case 1:
			// analogWrite(motor_pin_1, map(motor_duty_cycle, 0, 100, 0, 255));
			digitalWrite(motor_pin_1, HIGH);
			delay(motor_delay);
			digitalWrite(motor_pin_1, LOW);
			break;
	}
}

void setup() {
	Serial.begin(9600);
	pinMode(botao_pin_1, INPUT);
	pinMode(motor_pin_1, OUTPUT);
	botao_1.attach(botao_pin_1);
	botao_1.interval(5);
	lcd.begin(16, 2);          // Inicializa display de 2 linhas x 16 colunas
	lcd.home();                // Posiciona cursor no canto superior esquerdo
	lcd.clear();               // Limpa a tela do LCD
	lcd.print("Insira o RA");  // Frase inicial
}

void loop() {
	float valor_recebido = 0; // Valor recebido da porta serial
	int j = 1, k = 10, byte_recebido = 0, decimal = 0,
	    espera_botao = 0, sinal_recebido = 10, timer = 0;

	while (Serial.available() > 0) { // Espera haver entrada serial
		// Loop para receber os bytes de sinal e o saldo
		byte_recebido = Serial.read();
		delay(20);

		switch (byte_recebido) {
			case 65:
				sinal_recebido = 0;
				byte_recebido = 1;
				break;
			case 66:
				sinal_recebido = 1;
				byte_recebido = 1;
				break;
			case 67:
				sinal_recebido = 2;
				byte_recebido = 1;
				break;
			case 68:
				sinal_recebido = 3;
				byte_recebido = 1;
				break;
			case 69:
				sinal_recebido = 4;
				byte_recebido = 1;
				break;
			case 70:
				sinal_recebido = 5;
				byte_recebido = 1;
				break;
			case 46:
				decimal = 1;
				break;
			default:
				if (byte_recebido >= 48 && byte_recebido <= 57) {
					if (!decimal) {
						valor_recebido *= 10;
						valor_recebido += (byte_recebido - 48);
					} else {
						valor_recebido += (byte_recebido - 48) / (float) k;
						k *= 10;
					}
					byte_recebido = 1;
				}
				break;
		}
	}
	if (byte_recebido) {
		switch (sinal_recebido) {
			case 0:
				lcd.clear();
				lcd.print("RA sem cadastro");
				lcd.setCursor(0, 1);
				lcd.print("Retire seu RA");
				sinal_recebido = 10;
				break;
			case 1:
				lcd.clear();
				lcd.print("Compra efetuada!");
				lcd.setCursor(0, 1);
				lcd.print("Processando...");
				processar_compra();
				lcd.clear();
				lcd.print("Compra efetuada!");
				lcd.setCursor(0, 1);
				lcd.print("Retire seu RA");
				sinal_recebido = 10;
				break;
			case 2:
				lcd.clear();
				lcd.print("Erro na compra");
				lcd.setCursor(0, 1);
				lcd.print("Retire seu RA");
				sinal_recebido = 10;
				break;
			case 3:
				lcd.clear();
				lcd.print("Insira o RA");
				sinal_recebido = 10;
				break;
			case 4:
				lcd.clear();
				lcd.print("Lendo saldo...");
				sinal_recebido = 10;
				break;
			case 5:
				lcd.clear();
				lcd.print("Comprando...");
				sinal_recebido = 10;
				break;
			default:
				lcd.clear();
				lcd.print("Saldo: ");
				lcd.print(valor_recebido);
				while (espera_botao == 0) {
					botao_1.update();
					timer++;
					if (timer >= 200) { // Se não apertar um botão em até 10 segundos, cancela a operação
						Serial.print(2);
						sinal_recebido = 10;
						espera_botao = 1;
					}
					if (RE(botao_1.read(), estado_botao)) { // Executa na rising edge
						Serial.print(1);
						item_selecionado = 1;
						espera_botao = 1;
						sinal_recebido = 10;
					}
					delay(50);
				}
				break;
		}
	}
}

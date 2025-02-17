import {
  Component,
  OnInit,
  AfterViewInit,
  ElementRef,
  ViewChild,
  HostListener
} from '@angular/core';

@Component({
  selector: 'app-arc-blur',
  template: `
    <div class="container">
      <!-- Fundo -->
      <div class="background"></div>

      <!-- Camada de Blur -->
      <div class="blur-layer" #blurLayer></div>

      <!-- Arco -->
      <div class="arc-container" #arcContainer>
        <img src="assets/arco.png" alt="Arco" />
        <div class="arc-overlay" #arcOverlay></div>
      </div>

      <!-- TEXTO INICIAL -->
      <div class="text-area" #textArea>
        <div class="text-line" id="textLine1">Chegou a hora de</div>
        <div class="text-line" id="textLine2">começar a utilizar sua</div>
        <div class="text-line" id="textLine3">conta Itaú Empresas</div>
        <button class="btn-continuar" (click)="onContinuarClick()">Continuar</button>
      </div>

      <!-- BOTÃO FECHAR (X) - FIXO NO CANTO SUPERIOR DIREITO -->
      <button class="close-btn" #closeNextContent (click)="onCloseNextContent()">X</button>

      <!-- PRÓXIMO CONTEÚDO (SEM CAIXA) -->
      <div class="next-content" #nextContent>
        <div class="nc-line" #ncLine1>
          Tem atividade disponível pra você aproveitar sua conta!
        </div>
        <div class="nc-line" #ncLine2>
          Que tal cadastrar sua chave Pix para receber pagamentos?
        </div>
        <button class="btn-pix" #btnPix (click)="onPixClick()">
          Cadastrar chave Pix
        </button>
      </div>
    </div>
  `,
  styles: [`
    /* RESET */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    html, body {
      width: 100%;
      height: 100%;
      font-family: Arial, sans-serif;
    }

    .container {
      position: relative;
      width: 100%;
      height: 100vh;
      overflow: hidden;
    }

    /* FUNDO */
    .background {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      /* Ajuste a imagem no assets se desejar */
      background: url("assets/img-intro-prontidao.png") center/cover no-repeat;
      z-index: 0;
    }

    /* CAMADA DE DESFOQUE */
    .blur-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: url("assets/img-intro-prontidao.png") center/cover no-repeat;
      filter: blur(0);
      transition: filter 0.8s ease;
      z-index: 1;
    }
    .blur-layer.blur-active {
      filter: blur(6px);
    }

    /* ARCO PNG */
    .arc-container {
      position: absolute;
      top: 2%;
      left: -10%;
      height: 100%;
      width: auto;
      transform: translateX(0);
      transition: transform 0.8s ease;
      z-index: 2;
    }
    .arc-container img {
      display: block;
      height: 100%;
      width: auto;
      object-fit: contain;
    }

    /* OVERLAY DO ARCO */
    .arc-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      background: linear-gradient(
        to right,
        rgba(255, 255, 255, 0.30) 0%,
        rgba(255, 255, 255, 0.15) 40%,
        rgba(255, 255, 255, 0)   100%
      );
      opacity: 0;
      transition: opacity 0.8s ease;
    }
    .arc-overlay.overlay-active {
      opacity: 1;
    }

    /* TEXTO INICIAL (POSIÇÃO FIXA) */
    .text-area {
      position: fixed;
      top: 220px;
      right: 160px;
      text-align: right;
      color: #fff;
      font-size: 20px;
      line-height: 1.2;
      z-index: 4;
      opacity: 1;
      transition: opacity 0.5s ease;
    }
    .text-area .text-line {
      margin-bottom: 5px;
    }
    .btn-continuar {
      margin-top: 10px;
      padding: 10px 16px;
      border: none;
      border-radius: 4px;
      background-color: #007bff;
      color: #fff;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    .btn-continuar:hover {
      background-color: #0069d9;
    }

    /* BOTÃO (X) NO CANTO SUPERIOR DIREITO DA TELA */
    .close-btn {
      position: fixed;
      top: 20px;
      right: 20px;
      background: transparent;
      border: none;
      font-size: 24px;
      color: #fff;
      cursor: pointer;
      z-index: 5;
      opacity: 0; /* fade-in depois */
      transition: opacity 0.5s ease;
    }

    /* PRÓXIMO CONTEÚDO (SEM CAIXA) */
    .next-content {
      position: fixed;
      top: 280px;
      right: 160px;
      z-index: 5;
      display: none; /* Oculto inicialmente */
      opacity: 0;
      transition: opacity 0.5s ease;
    }
    .next-content.show {
      display: block;
    }
    .next-content.fade-in {
      opacity: 1;
    }

    .nc-line {
      color: #fff;
      font-size: 20px;
      line-height: 1.4;
      margin-bottom: 10px;
      opacity: 0; /* fade-in depois */
      transition: opacity 0.5s ease;
    }

    .btn-pix {
      margin-top: 10px;
      padding: 10px 16px;
      border: none;
      border-radius: 4px;
      background-color: #ff6600;
      color: #fff;
      font-size: 16px;
      cursor: pointer;
      opacity: 0; /* fade-in depois */
      transition: background-color 0.3s, opacity 0.5s ease;
    }
    .btn-pix:hover {
      background-color: #e85700;
    }
  `]
})
export class ArcBlurComponent implements OnInit, AfterViewInit {

  /* 
    "ViewChild" permite acessar elementos do template.
    O 'static: false' (padrão) significa que só teremos acesso 
    após o "ngAfterViewInit".
  */

  @ViewChild('blurLayer') blurLayer!: ElementRef<HTMLDivElement>;
  @ViewChild('arcContainer') arcContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('arcOverlay') arcOverlay!: ElementRef<HTMLDivElement>;

  @ViewChild('textArea') textArea!: ElementRef<HTMLDivElement>;
  @ViewChild('closeNextContent') closeNextContent!: ElementRef<HTMLButtonElement>;
  @ViewChild('nextContent') nextContent!: ElementRef<HTMLDivElement>;

  @ViewChild('ncLine1') ncLine1!: ElementRef<HTMLDivElement>;
  @ViewChild('ncLine2') ncLine2!: ElementRef<HTMLDivElement>;
  @ViewChild('btnPix') btnPix!: ElementRef<HTMLButtonElement>;

  movedRight = false;

  constructor() { }

  ngOnInit(): void {
    // Inicialização que não depende de ViewChild
  }

  ngAfterViewInit(): void {
    // Tudo que depende de @ViewChild já está disponível aqui
  }

  // === EVENTO CLIQUE NO BOTÃO "CONTINUAR" ===
  onContinuarClick(): void {
    // 1) Fade out do texto inicial
    this.textArea.nativeElement.style.opacity = '0';
    setTimeout(() => {
      this.textArea.nativeElement.style.display = 'none';
    }, 500);

    // 2) Move o arco para a direita (com blur)
    this.moveArcoToRight();

    // 3) Após 0.8s, exibe o próximo conteúdo
    setTimeout(() => {
      this.showNextContent();
    }, 800);
  }

  // === MOVE ARCO PARA DIREITA + BLUR ===
  moveArcoToRight(): void {
    // Largura aproximada do arco (ajuste conforme necessário)
    const arcWidth = 650;
    const distance = window.innerWidth - arcWidth;

    // Anima o arco
    this.arcContainer.nativeElement.style.transform = `translateX(${distance}px)`;

    // Ativa blur do fundo
    this.blurLayer.nativeElement.classList.add('blur-active');
    // Ativa gradiente dentro do arco
    this.arcOverlay.nativeElement.classList.add('overlay-active');

    this.movedRight = true;
  }

  // === MOSTRAR O PRÓXIMO CONTEÚDO ===
  showNextContent(): void {
    // 1) Torna o container visível
    this.nextContent.nativeElement.classList.add('show');
    setTimeout(() => {
      this.nextContent.nativeElement.classList.add('fade-in');
    }, 50);

    // 2) Botão X (close) fade in
    setTimeout(() => {
      this.closeNextContent.nativeElement.style.opacity = '1';
    }, 200);

    // 3) Linhas de texto e botão Pix em sequência de 2s
    // 1a linha (após 2s)
    setTimeout(() => {
      this.ncLine1.nativeElement.style.opacity = '1';
    }, 2000);

    // 2a linha (após 4s)
    setTimeout(() => {
      this.ncLine2.nativeElement.style.opacity = '1';
    }, 4000);

    // Botão Pix (após 6s)
    setTimeout(() => {
      this.btnPix.nativeElement.style.opacity = '1';
    }, 6000);
  }

  // === FECHAR O PRÓXIMO CONTEÚDO (BOTÃO X) ===
  onCloseNextContent(): void {
    // 1) Fade out de tudo
    this.closeNextContent.nativeElement.style.opacity = '0';
    this.ncLine1.nativeElement.style.opacity = '0';
    this.ncLine2.nativeElement.style.opacity = '0';
    this.btnPix.nativeElement.style.opacity = '0';

    // 2) Fade out do container
    this.nextContent.nativeElement.classList.remove('fade-in');

    // 3) Após 0.5s, esconder (display: none)
    setTimeout(() => {
      this.nextContent.nativeElement.classList.remove('show');
    }, 500);
  }

  // === CLIQUE NO BOTÃO PIX ===
  onPixClick(): void {
    alert("Você clicou em Cadastrar chave Pix!");
  }

  // === RECALCULAR POSIÇÃO SE REDIMENSIONAR A TELA ===
  @HostListener('window:resize', ['$event'])
  onResize() {
    if (this.movedRight) {
      const arcWidth = 650;
      const distance = window.innerWidth - arcWidth;
      this.arcContainer.nativeElement.style.transform = `translateX(${distance}px)`;
    }
  }

}

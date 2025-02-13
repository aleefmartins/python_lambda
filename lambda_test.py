<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Arco + Blur + Gradiente Claro</title>

  <style>
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

    /* FUNDO normal */
    .background {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: url("img-intro-prontidao.png") center/cover no-repeat;
      z-index: 0;
    }

    /* CAMADA DE DESFOQUE (desligada no início) */
    .blur-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: url("img-intro-prontidao.png") center/cover no-repeat;
      filter: blur(0);
      transition: filter 0.8s ease;  /* sincroniza com animação do arco */
      z-index: 1;
    }
    .blur-layer.blur-active {
      filter: blur(6px);
    }

    /* ARCO PNG */
    .arc-container {
      position: absolute;
      top: 0;
      left: 0;
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

    /*
     * OVERLAY DENTRO DO ARCO
     * Ajuste aqui o GRADIENTE para ficar mais claro/cinza translúcido
     */
    .arc-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      /* Exemplo: gradiente de um cinza / branco translúcido para transparente */
      background: linear-gradient(
        to right, 
        rgba(255, 255, 255, 0.30) 0%,   /* parte mais opaca do lado esquerdo */
        rgba(255, 255, 255, 0.15) 40%,  /* intermediário */
        rgba(255, 255, 255, 0)   100%   /* transparente no lado direito */
      );
      opacity: 0;
      transition: opacity 0.8s ease;
    }
    .arc-overlay.overlay-active {
      opacity: 1;
    }

    /* BOTÃO */
    .btn-toggle {
      position: absolute;
      bottom: 20px;
      right: 20px;
      z-index: 3;
      padding: 12px 20px;
      border: none;
      border-radius: 4px;
      background-color: #ff6600;
      color: #fff;
      font-size: 16px;
      cursor: pointer;
      outline: none;
      transition: background-color 0.3s;
    }
    .btn-toggle:hover {
      background-color: #e85700;
    }

  </style>
</head>
<body>
  <div class="container">
    <!-- Fundo normal -->
    <div class="background"></div>

    <!-- Layer que receberá o blur -->
    <div class="blur-layer" id="blurLayer"></div>

    <!-- Arco PNG -->
    <div class="arc-container" id="arcContainer">
      <img src="arco.png" alt="Arco" />
      <!-- Overlay gradiente claro dentro do arco -->
      <div class="arc-overlay" id="arcOverlay"></div>
    </div>

    <!-- Botão -->
    <button class="btn-toggle" id="btnToggleArc">Mover Arco</button>
  </div>

  <script>
    const arcContainer = document.getElementById('arcContainer');
    const arcOverlay   = document.getElementById('arcOverlay');
    const blurLayer    = document.getElementById('blurLayer');
    const btnToggleArc = document.getElementById('btnToggleArc');

    let movedRight = false;

    // Clicar no botão → anima arco + blur + overlay
    btnToggleArc.addEventListener('click', () => {
      if (!movedRight) {
        moveArcoToRight();
      } else {
        moveArcoToLeft();
      }
    });

    function moveArcoToRight() {
      const arcWidth = arcContainer.offsetWidth;
      const distance = window.innerWidth - arcWidth;
      arcContainer.style.transform = `translateX(${distance}px)`;

      // Ativa blur do fundo
      blurLayer.classList.add('blur-active');
      // Ativa gradiente dentro do arco
      arcOverlay.classList.add('overlay-active');

      movedRight = true;
    }

    function moveArcoToLeft() {
      arcContainer.style.transform = 'translateX(0)';

      // Desativa blur
      blurLayer.classList.remove('blur-active');
      // Desativa gradiente
      arcOverlay.classList.remove('overlay-active');

      movedRight = false;
    }

    // Se a tela redimensionar com o arco na direita, recalcular
    window.addEventListener('resize', () => {
      if (movedRight) {
        const arcWidth = arcContainer.offsetWidth;
        const distance = window.innerWidth - arcWidth;
        arcContainer.style.transform = `translateX(${distance}px)`;
      }
    });
  </script>
</body>
</html>

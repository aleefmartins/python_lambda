/* tslint:disable:no-unsafe-any */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ElementRef, NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';
import { WelcomeComponent } from './welcome.component';

// Ajuste esses imports para o real local dos serviços:
import { CadastrarPixService } from '../cadastrar-pix.service'; 
import { TracksServiceWeb } from '../tracks.service-web';
// Caso exista um RouterService:
import { RouterService } from '../router.service';

/* ──────────────── FAKES / STUBS ──────────────── */
class FakeCadastrarPixService {
  cadastrarChavePix = jest.fn(() => of({ ok: true }));
}
class FakeTracksServiceWeb {
  clickEvent = jest.fn();
  pageLoad   = jest.fn();
}
/** Se seu componente injeta RouterService, faça um stub: */
class FakeRouterService {
  // Adicione aqui qualquer método que o componente use
  navigate = jest.fn();
}

/* Cria algo que simula HTMLElement / HTMLImageElement */
function fakeDomEl(): any {
  return {
    style:         {},
    classList:     { add: jest.fn(), remove: jest.fn(), contains: jest.fn() },
    querySelector: jest.fn(() => fakeDomEl()),
    addEventListener: jest.fn((_, cb) => cb && cb()),
    src: '',
  };
}

/* Util para preencher manualmente as dezenas de @ViewChilds */
function assignFakeEl<T extends object>(target: T, prop: keyof T) {
  (target as any)[prop] = new ElementRef(fakeDomEl());
}

describe('WelcomeComponent – high‑coverage spec', () => {
  let component: WelcomeComponent;
  let fixture: ComponentFixture<WelcomeComponent>;
  let tracks: FakeTracksServiceWeb;

  beforeAll(() => {
    jest.useFakeTimers();
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [WelcomeComponent],
      /** IMPORTANTE: aqui mapear o serviço real → fake/stub */
      providers: [
        { provide: CadastrarPixService, useClass: FakeCadastrarPixService },
        { provide: TracksServiceWeb,    useClass: FakeTracksServiceWeb },
        { provide: RouterService,       useClass: FakeRouterService }, 
        // Se você não usa RouterService, pode remover essa linha
      ],
      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();

    fixture   = TestBed.createComponent(WelcomeComponent);
    component = fixture.componentInstance;
    tracks    = TestBed.inject(TracksServiceWeb) as unknown as FakeTracksServiceWeb;

    // Preenche manualmente @ViewChilds do componente
    [
      'arcContainer', 'textArea', 'btnContinuar', 'nextContent',
      'textLine1', 'textLine2', 'textLine3', 'lineKey',
      'line1', 'line2', 'line3', 'btnPix', 'closeButton'
    ].forEach(p => assignFakeEl(component as any, p as any));

    fixture.detectChanges(); // chama ngOnInit + ngAfterViewInit
  });

  /* ─────────────── ngOnInit / AfterViewInit ─────────────── */
  it('deve chamar pageLoad no ngOnInit e programar carregamento de textos', () => {
    expect(tracks.pageLoad).toHaveBeenCalledTimes(1);

    jest.advanceTimersByTime(600); // loadingTextInicial
    expect(component.textLine1.nativeElement.style.opacity).toBe('1');

    jest.advanceTimersByTime(2400); // loadingTextTwo (total 3000ms)
    expect(component.textLine2.nativeElement.style.opacity).toBe('1');
  });

  it('deve ajustar a largura da imagem em AfterViewInit', () => {
    const img = component.arcContainer.nativeElement.querySelector('img') as any;
    expect(img.style.width).toBeDefined();
    expect(img.style.height).toBeDefined();
  });

  /* ─────────────── adjustImageWidth branch ─────────────── */
  it('adjustImageWidth usa baseHeight diferente quando glassActivate = true', () => {
    component.glassActivate = true;
    component.adjustImageWidth();
    const img = component.arcContainer.nativeElement.querySelector('img') as any;
    expect(img.style.height).toContain('px');
  });

  /* ─────────────── onContinuarClick ─────────────── */
  it('onContinuarClick oculta textArea e move arco', () => {
    const moveSpy = jest
      .spyOn(component as any, 'moveArcoToRight') // ← se o método for moveArcToRight ou outro, troque aqui
      .mockImplementation(() => {});

    component.onContinuarClick();

    const taStyle = component.textArea.nativeElement.style;
    expect(taStyle.opacity).toBe('0');

    jest.advanceTimersByTime(500);
    expect(taStyle.display).toBe('none');
    expect(moveSpy).toHaveBeenCalled();
    expect(tracks.clickEvent).toHaveBeenCalled();
  });

  /* ─────────────── moveArcoToRight + showNextContent ─────────────── */
  it('moveArcoToRight altera movedRight, aplica blur e exibe próximo conteúdo', () => {
    const content = fakeDomEl();
    document.querySelector = jest.fn(() => content);

    // Se o método é 'moveArcToRight', adapte o nome
    component.moveArcoToRight();

    expect(component.movedRight).toBe(true);
    expect(content.classList.add).toHaveBeenCalledWith('blur-background');
    // tracks.pageLoad foi chamada 1x no onInit e 1x agora → total 2
    expect(tracks.pageLoad).toHaveBeenCalledTimes(2);

    jest.advanceTimersByTime(3000); // showNextContent
    expect(component.nextContent.nativeElement.classList.add).toHaveBeenCalledWith('show');
  });

  /* ─────────────── openModal / onModalClose ─────────────── */
  it('openModal e onModalClose alternam isModalOpen e disparam tracks', () => {
    component.openModal();
    expect(component.isModalOpen).toBe(true);

    component.onModalClose();
    expect(component.isModalOpen).toBe(false);

    expect(tracks.clickEvent).toHaveBeenCalledTimes(2);
  });

  /* ─────────────── onResize branch (movedRight = true) ─────────────── */
  it('onResize ajusta translateX quando movedRight = true', () => {
    component.movedRight = true;
    component.onResize();
    const arcStyle = component.arcContainer.nativeElement.style;
    expect(arcStyle.transform).toContain('translateX');
  });
});

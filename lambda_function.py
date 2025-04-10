/* tslint:disable:no-unsafe-any */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ElementRef, NO_ERRORS_SCHEMA } from '@angular/core';
import { of } from 'rxjs';
import { WelcomeComponent } from './welcome.component';

/* ──────────────── FAKES / STUBS ──────────────── */
class FakeCadastrarPixService {
  cadastrarChavePix = jest.fn(() => of({ ok: true }));
}
class FakeTracksServiceWeb {
  clickEvent  = jest.fn();
  pageLoad    = jest.fn();
}

/* gera um objeto que simula HTMLElement / HTMLImageElement */
function fakeDomEl(): any {
  return {
    style:         {},
    classList:     { add: jest.fn(), remove: jest.fn(), contains: jest.fn() },
    querySelector: jest.fn(() => fakeDomEl()),
    addEventListener: jest.fn((_, cb) => cb && cb()), // chama callback imediatamente
    src: '',
  };
}

/* util para preencher rapidamente @ViewChilds */
function assignFakeEl<T extends object>(target: T, prop: keyof T) {
  (target as any)[prop] = new ElementRef(fakeDomEl());
}

/* ─────────────────────────────────────────────── */

describe('WelcomeComponent – high‑coverage spec', () => {
  let component: WelcomeComponent;
  let fixture: ComponentFixture<WelcomeComponent>;
  let tracks: FakeTracksServiceWeb;

  beforeAll(() => {
    jest.useFakeTimers();         // controlamos todos os setTimeout
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [WelcomeComponent],
      providers: [
        { provide: FakeCadastrarPixService, useClass: FakeCadastrarPixService },
        { provide: FakeTracksServiceWeb,    useClass: FakeTracksServiceWeb  },
      ],
      schemas: [NO_ERRORS_SCHEMA], // ignora o template real
    }).compileComponents();

    fixture   = TestBed.createComponent(WelcomeComponent);
    component = fixture.componentInstance;
    tracks    = TestBed.inject(FakeTracksServiceWeb);

    /* preenche manualmente as dezenas de @ViewChilds */
    [
      'arcContainer', 'textArea', 'btnContinuar', 'nextContent',
      'textLine1', 'textLine2', 'textLine3', 'lineKey',
      'line1', 'line2', 'line3', 'btnPix', 'closeButton'
    ].forEach(p => assignFakeEl(component as any, p as any));

    fixture.detectChanges(); // ngOnInit
  });

  /* ─────────────── ngOnInit / AfterViewInit ─────────────── */
  it('deve chamar pageLoad no ngOnInit e programar carregamento de textos', () => {
    expect(tracks.pageLoad).toHaveBeenCalledTimes(1);

    // avança 600 ms → loadingTextInicial
    jest.advanceTimersByTime(600);
    expect((component as any).textLine1.nativeElement.style.opacity).toBe('1');

    // avança até 3000 ms → loadingTextTwo
    jest.advanceTimersByTime(2400);
    expect((component as any).textLine2.nativeElement.style.opacity).toBe('1');
  });

  it('deve ajustar a largura da imagem em AfterViewInit', () => {
    // após fixture.detectChanges o Angular já chamou ngAfterViewInit
    const img =
      (component.arcContainer.nativeElement.querySelector('img') as any) || {};
    expect(img.style.width).toBeDefined();
    expect(img.style.height).toBeDefined();
  });

  /* ─────────────── adjustImageWidth branches ─────────────── */
  it('adjustImageWidth usa baseHeight diferente quando glassActivate = true', () => {
    component.glassActivate = true;
    component.adjustImageWidth();
    const img = component.arcContainer.nativeElement.querySelector('img') as any;
    expect(img.style.height).toContain('px');
  });

  /* ─────────────── onContinuarClick ─────────────── */
  it('onContinuarClick oculta textArea e move arco', () => {
    const moveSpy = jest.spyOn(component, 'moveArcToRight').mockImplementation();
    component.onContinuarClick();

    const taStyle = component.textArea.nativeElement.style;
    expect(taStyle.opacity).toBe('0');

    // dispara timeout de 500 ms → display none
    jest.advanceTimersByTime(500);
    expect(taStyle.display).toBe('none');
    expect(moveSpy).toHaveBeenCalled();
    expect(tracks.clickEvent).toHaveBeenCalled();
  });

  /* ─────────────── moveArcToRight + showNextContent ─────────────── */
  it('moveArcToRight altera movedRight, aplica blur e exibe próximo conteúdo', () => {
    const content = fakeDomEl();
    document.querySelector = jest.fn(() => content); // captura do querySelector interno

    component.moveArcToRight();

    expect(component.movedRight).toBe(true);
    expect(content.classList.add).toHaveBeenCalledWith('blur-background');
    expect(tracks.pageLoad).toHaveBeenCalledTimes(2); // uma do ngOnInit + uma aqui

    // showNextContent é disparado após 3000 ms
    jest.advanceTimersByTime(3000);
    expect(component.nextContent.nativeElement.classList.add).toHaveBeenCalledWith('show');
  });

  /* ─────────────── openModal / onModalClose ─────────────── */
  it('openModal e onModalClose alternam isModalOpen e disparam eventos de track', () => {
    component.isModalOpen = false;
    component.openModal();
    expect(component.isModalOpen).toBe(true);
    expect(tracks.clickEvent).toHaveBeenCalled();

    component.onModalClose();
    expect(component.isModalOpen).toBe(false);
    expect(tracks.clickEvent).toHaveBeenCalledTimes(2);
  });

  /* ─────────────── onResize branch (movedRight = true) ─────────────── */
  it('onResize ajusta translateX quando movedRight = true', () => {
    component.movedRight = true;
    component.onResize(); // chama adjustImageWidth + movimentação
    const arcStyle = component.arcContainer.nativeElement.style;
    expect(arcStyle.transform).toContain('translateX');
  });
});

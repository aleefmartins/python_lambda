import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';

/* -------- Stub global para o jsdom não quebrar no window.close -------- */
Object.defineProperty(window, 'close', {
  configurable: true,
  writable: true,
  value: jest.fn(),
});
/* ---------------------------------------------------------------------- */

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [RouterTestingModule],
      providers: [{ provide: Router, useValue: { navigate: jest.fn() } }],
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
  });

  /* ------------------------------------------------------------------
   *  TESTES JÁ EXISTENTES (alguns ainda mockam loadScriptGA4)
   * ----------------------------------------------------------------- */
  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should call loadScriptGA4 on ngOnInit', () => {
    const spy = jest
      .spyOn(component, 'loadScriptGA4')
      .mockImplementation(cb => cb());
    component.ngOnInit();
    expect(spy).toHaveBeenCalled();
  });

  it('should navigate to / on successful script load', () => {
    jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb());
    const navSpy = jest.spyOn(router, 'navigate');
    component.ngOnInit();
    expect(navSpy).toHaveBeenCalledWith(['/']);
  });

  it('should handle script load error', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    jest
      .spyOn(component, 'loadScriptGA4')
      .mockImplementation(cb => cb(new Error('Test Error')));
    component.ngOnInit();
    expect(consoleSpy).toHaveBeenCalledWith(
      'Erro ao carregar o script:',
      'Test Error',
    );
  });

  /* ------------------------------------------------------------------
   *  TESTES DO injectScriptGA  (mantidos)
   * ----------------------------------------------------------------- */
  it('should inject scripts into iframe', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    const callback = jest.fn();
    component.injectScriptGA(iframe, callback);

    Array.from(iframe.contentDocument?.getElementsByTagName('script') || []).forEach(
      s => s.dispatchEvent(new Event('load')),
    );

    expect(callback).toHaveBeenCalled();
  });

  it('should handle iframe document access error', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();
    component.injectScriptGA({} as any, cb);
    expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(cb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle script load error inside injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    jest
      .spyOn(iframe.contentDocument!, 'createElement')
      .mockImplementation(() => {
        const sc = document.createElement('script');
        sc.onerror = null;
        return sc;
      });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();

    component.injectScriptGA(iframe, cb);
    Array.from(iframe.contentDocument!.getElementsByTagName('script')).forEach(s =>
      s.dispatchEvent(new Event('error')),
    );

    expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(cb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle ItaúDigitalAnalytics not available inside injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();

    component.injectScriptGA(iframe, cb);
    Array.from(iframe.contentDocument!.getElementsByTagName('script')).forEach(s =>
      s.dispatchEvent(new Event('load')),
    );

    expect(consoleSpy).toHaveBeenCalledWith(
      'ItaúDigitalAnalytics não está disponível!',
    );
    expect(cb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle null contentDocument', () => {
    const iframe = document.createElement('iframe');
    Object.defineProperty(iframe, 'contentDocument', { value: null });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();

    component.injectScriptGA(iframe, cb);
    expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(cb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle contentWindow.document undefined', () => {
    const iframe = document.createElement('iframe');
    Object.defineProperty(iframe, 'contentWindow', { value: {}, writable: true });

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();

    component.injectScriptGA(iframe, cb);
    expect(consoleSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(cb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should finish successfully when ItaúDigitalAnalytics is present', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    const cb = jest.fn();
    component.injectScriptGA(iframe, cb);

    (iframe.contentWindow as any).ItaúDigitalAnalytics = {};
    Array.from(iframe.contentDocument!.getElementsByTagName('script')).forEach(s =>
      s.dispatchEvent(new Event('load')),
    );

    expect(cb).toHaveBeenCalled();
  });

  /* ------------------------------------------------------------------
   *  ⬇️  NOVOS TESTES – cobrem todas as linhas de loadScriptGA4  ⬇️
   * ----------------------------------------------------------------- */

  it('loadScriptGA4 – fluxo de sucesso', () => {
    const outerCb = jest.fn();

    // força o injectScriptGA a “dar certo”
    const injectSpy = jest
      .spyOn(component, 'injectScriptGA')
      .mockImplementation((_, cb) => cb());

    component.loadScriptGA4(outerCb);

    // pega o iframe criado e dispara o onload
    const iframe = document.getElementById('scriptIframe') as HTMLIFrameElement;
    Object.defineProperty(iframe, 'contentWindow', {
      value: { ItaúDigitalAnalytics: {} },
      writable: true,
    });
    iframe.onload!(new Event('load'));

    expect(injectSpy).toHaveBeenCalled();
    expect((window as any).ItaúDigitalAnalytics).toBeDefined();
    expect(outerCb).toHaveBeenCalled();
  });

  it('loadScriptGA4 – erro vindo do injectScriptGA', () => {
    const outerCb = jest.fn();
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    jest
      .spyOn(component, 'injectScriptGA')
      .mockImplementation((_, cb) => cb(new Error('boom')));

    component.loadScriptGA4(outerCb);

    const iframe = document.getElementById('scriptIframe') as HTMLIFrameElement;
    iframe.onload!(new Event('load'));

    expect(consoleSpy).toHaveBeenCalledWith('Erro ao carregar o script:', expect.any(Error));
    expect(outerCb).toHaveBeenCalledWith(expect.any(Error));
  });

  it('loadScriptGA4 – ItaúDigitalAnalytics ausente', () => {
    const outerCb = jest.fn();
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    jest
      .spyOn(component, 'injectScriptGA')
      .mockImplementation((_, cb) => cb()); // sucesso na injeção

    component.loadScriptGA4(outerCb);

    const iframe = document.getElementById('scriptIframe') as HTMLIFrameElement;
    Object.defineProperty(iframe, 'contentWindow', {
      value: {}, // sem ItaúDigitalAnalytics
      writable: true,
    });
    iframe.onload!(new Event('load'));

    expect(consoleSpy).toHaveBeenCalledWith('ItaúDigitalAnalytics não está disponível!');
    expect(outerCb).toHaveBeenCalledWith(expect.any(Error));
  });
});

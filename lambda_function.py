import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';

/* ----------  ⬇️  FIX contra o TypeError: Window.close  ⬇️ ---------- */
Object.defineProperty(window, 'close', {
  configurable: true,
  writable: true,
  value: jest.fn(),          // evita “this[i].close is not a function”
});
/* ------------------------------------------------------------------- */

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

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should call loadScriptGA4 on ngOnInit', () => {
    const spy = jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb());
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
    jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb(new Error('Test Error')));
    component.ngOnInit();
    expect(consoleSpy).toHaveBeenCalledWith('Erro ao carregar o script:', 'Test Error');
  });

  it('should inject scripts into iframe', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    const callback = jest.fn();
    component.injectScriptGA(iframe, callback);

    Array.from(iframe.contentDocument?.getElementsByTagName('script') || []).forEach(s =>
      s.dispatchEvent(new Event('load')),
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

    jest.spyOn(iframe.contentDocument!, 'createElement').mockImplementation(() => {
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

  it('should handle ItaúDigitalAnalytics not available', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const cb = jest.fn();

    component.injectScriptGA(iframe, cb);
    Array.from(iframe.contentDocument!.getElementsByTagName('script')).forEach(s =>
      s.dispatchEvent(new Event('load')),
    );

    expect(consoleSpy).toHaveBeenCalledWith('ItaúDigitalAnalytics não está disponível!');
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

    // coloca o objeto antes de disparar o load
    (iframe.contentWindow as any).ItaúDigitalAnalytics = {};
    Array.from(iframe.contentDocument!.getElementsByTagName('script')).forEach(s =>
      s.dispatchEvent(new Event('load')),
    );

    expect(cb).toHaveBeenCalled();
  });
});

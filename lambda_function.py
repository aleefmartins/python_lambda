import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { AppComponent } from './app.component';
import { RouterTestingModule } from '@angular/router/testing';

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AppComponent],
      imports: [RouterTestingModule],
      providers: [
        { provide: Router, useValue: { navigate: jest.fn() } }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should call loadScriptGA4 on ngOnInit', () => {
    const loadScriptSpy = jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb());
    component.ngOnInit();
    expect(loadScriptSpy).toHaveBeenCalled();
  });

  it('should navigate to / on successful script load', () => {
    jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb());
    const routerSpy = jest.spyOn(router, 'navigate');
    component.ngOnInit();
    expect(routerSpy).toHaveBeenCalledWith(['/']);
  });

  it('should handle script load error', () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(component, 'loadScriptGA4').mockImplementation(cb => cb(new Error('Test Error')));
    component.ngOnInit();
    expect(consoleErrorSpy).toHaveBeenCalledWith('Erro ao carregar o script:', 'Test Error');
  });

  it('should inject scripts into iframe', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);
    const callback = jest.fn();
    component.injectScriptGA(iframe, callback);

    const scripts = iframe.contentDocument?.getElementsByTagName('script') || [];
    Array.from(scripts).forEach(script => {
      script.dispatchEvent(new Event('load'));
    });

    expect(callback).toHaveBeenCalled();
  });

  it('should handle iframe document access error', () => {
    const callback = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    component.injectScriptGA({} as HTMLIFrameElement, callback);
    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(callback).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle script load error in injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);
    const callback = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    jest.spyOn(iframe.contentDocument!, 'createElement').mockImplementation(() => {
      const script = document.createElement('script');
      script.onerror = null;
      return script;
    });

    component.injectScriptGA(iframe, callback);
    const scripts = iframe.contentDocument!.getElementsByTagName('script');
    Array.from(scripts).forEach(script => {
      script.dispatchEvent(new Event('error'));
    });

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(callback).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle ItaúDigitalAnalytics not available', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);
    const callback = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    component.injectScriptGA(iframe, callback);
    const scripts = iframe.contentDocument!.getElementsByTagName('script');
    Array.from(scripts).forEach(script => {
      script.dispatchEvent(new Event('load'));
    });

    expect(consoleErrorSpy).toHaveBeenCalledWith('ItaúDigitalAnalytics não está disponível!');
    expect(callback).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle null contentDocument in injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    Object.defineProperty(iframe, 'contentDocument', { value: null });
    const callback = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    component.injectScriptGA(iframe, callback);
    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(callback).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle contentWindow.document undefined in injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);

    Object.defineProperty(iframe, 'contentWindow', {
      value: {},
      writable: true
    });

    const callback = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    component.injectScriptGA(iframe, callback);

    expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(Error));
    expect(callback).toHaveBeenCalledWith(expect.any(Error));
  });

  it('should handle successful script load in injectScriptGA', () => {
    const iframe = document.createElement('iframe');
    document.body.appendChild(iframe);
    const callback = jest.fn();

    component.injectScriptGA(iframe, callback);
    const scripts = iframe.contentDocument!.getElementsByTagName('script');
    Array.from(scripts).forEach(script => {
      (iframe.contentWindow as any).ItaúDigitalAnalytics = {};
      script.dispatchEvent(new Event('load'));
    });

    expect(callback).toHaveBeenCalled();
  });
});

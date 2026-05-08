/// <reference types="vite/client" />

declare global {
    interface Window {
        L2Dwidget?: {
            alertText: (text: string, probability?: number, duration?: number) => void;
            init: (config: any) => void;
        };
    }

    const L2Dwidget: Window['L2Dwidget'];
}

export { };


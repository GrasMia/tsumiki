export function throttle<T extends (...args: any[]) => any>(func: T, delay: number): (...args: Parameters<T>) => ReturnType<T> {
    let lastCall = 0;
    return (...args: Parameters<T>) => {
        const now = Date.now();
        if (now - lastCall >= delay) {
            lastCall = now;
            return func(...args);
        }
    }
}

export function debounce<T extends (...args: any[]) => any>(func: T, delay: number):
    (...args: Parameters<T>) => void {

    let debounceTimerId: ReturnType<typeof setTimeout> | undefined;
    return (...args: Parameters<T>) => {
        if (debounceTimerId) {
            clearTimeout(debounceTimerId);
        }
        debounceTimerId = setTimeout(() => {
            func(...args);
            debounceTimerId = undefined;
        }, delay);
    };
}
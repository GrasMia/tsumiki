export const preventSpace = (e: KeyboardEvent) => {
    if (e.key === ' ' || e.code === 'Space') {
        e.preventDefault();
    }
};

export const formatStorage = (value: number) => {
    if (!value) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = value;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`;
};
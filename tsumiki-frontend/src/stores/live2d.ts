export function live2dAlert(text: string, probability?: number, duration?: number) {
    if (L2Dwidget?.alertText) {
        L2Dwidget.alertText(text, probability, duration);
    }
}

export function live2dAlertPrompt(text: string, probability?: number, duration?: number) {
    if (L2Dwidget?.alertText) {
        const RAND = Math.random()
        text += (RAND >= 2 / 3 ? '' : RAND >= 1 / 3 ? 'だよ' : 'なのだ');
        L2Dwidget.alertText(text, probability, duration);
    }
}

export function live2dAlertRhetorical(text: string, probability?: number, duration?: number) {
    if (L2Dwidget?.alertText) {
        const RAND = Math.random()
        text += (RAND >= 2 / 3 ? 'を入力してね' : RAND >= 1 / 3 ? 'が入力されていないよ' : 'まだ入力してないもん');
        L2Dwidget.alertText(text, probability, duration);
    }
}
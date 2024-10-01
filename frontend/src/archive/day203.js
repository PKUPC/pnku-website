function makeCurrentState(puzzleDetail) {
    const gameStartSeconds = Math.floor(new Date('2024-07-19T20:00:00+08:00').getTime() / 1000);
    const currentSeconds = Math.floor(Date.now() / 1000);
    const hours = Math.floor((currentSeconds - gameStartSeconds) / 3600);
    const id1 = (hours % 6) + 1;
    const id2 = (hours % 8) + 1;
    const id3 = (hours % 4) + 1;
    const id4 = (hours % 5) + 1;
    const id5 = (hours % 7) + 1;
    const id6 = (hours % 9) + 1;

    const fig1 = `media/puzzle/day2_03/SUB1/SUB1-${id1}.webp`;
    const fig2 = `media/puzzle/day2_03/SUB2/SUB2-${id2}.webp`;
    const fig3 = `media/puzzle/day2_03/SUB3/SUB3-${id3}.webp`;
    const fig4 = `media/puzzle/day2_03/SUB4/SUB4-${id4}.webp`;
    const fig5 = `media/puzzle/day2_03/SUB5_v3/SUB5-${id5}.webp`;

    const fig6 = `media/puzzle/day2_03/SUB6_v2/SUB6-${id6}.webp`;
    let result = JSON.parse(JSON.stringify(puzzleDetail));
    result.desc = result.desc.replace('REPLACEME1', fig1);
    result.desc = result.desc.replace('REPLACEME2', fig2);
    result.desc = result.desc.replace('REPLACEME3', fig3);
    result.desc = result.desc.replace('REPLACEME4', fig4);
    result.desc = result.desc.replace('REPLACEME5', fig5);
    result.desc = result.desc.replace('REPLACEME6', fig6);

    console.log(result.desc);

    return result;
}

export { makeCurrentState };

/**
 * @name EnlargeEmojis
 * @version 1.0.0
 * @description A BetterDiscord plugin to enlarge emojis in the chat.
 */
 
module.exports = class EnlargeEmojis {
    constructor() {}

    start() {
        BdApi.injectCSS("EnlargeEmojisCSS", `
            .emoji {
                width: 20px !important; 
                height: 100px !important; 
                display: inline-block;
                vertical-align: middle;
                padding-left: 10px;
                padding-right: 10px; 
            }
        `);
    }

    stop() {
        BdApi.clearCSS("EnlargeEmojisCSS");
    }
}

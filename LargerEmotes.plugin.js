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
                width: 40px !important; /* Increase the width of the emoji */
                height: 50px !important; /* Increase the height of the emoji */
                display: inline-block;
                vertical-align: middle;
                padding-left: 0px; /* Add left padding */
                padding-right: 0px; /* Add right padding */
            }
        `);
    }

    stop() {
        BdApi.clearCSS("EnlargeEmojisCSS");
    }
}

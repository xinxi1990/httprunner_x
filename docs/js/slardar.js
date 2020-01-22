
(function(i,s,o,g,r,a,m){i["SlardarMonitorObject"]=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date;a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,"script","https://i.snssdk.com/slardar/sdk.js?bid=httprunner_x","Slardar");
window.Slardar('config', {
    sampleRate: 1,
    bid: 'httprunner_x',
    ignoreAjax: [],
    ignoreStatic: [],
    hookFetch: true,
    enableSizeStats: true
});
window.Slardar('send', 'pageview');
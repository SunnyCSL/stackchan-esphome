import{B as o,r as t,_ as e,e as i,t as s,n as r,s as a,x as l}from"./index-zaYCB7m6.js";import"./c.CzGI896K.js";import{o as n,a as c}from"./c.pzUM4vYj.js";import"./c.B41VBpbv.js";import"./c.Dfz7XRSh.js";import"./c.BsE5xiOP.js";import"./c.Ceriyo_r.js";import"./c.JensFMpi.js";import"./c.ByTXXitT.js";let p=class extends a{constructor(){super(...arguments),this.downloadFactoryFirmware=!0}render(){return l`
      <esphome-process-dialog
        .heading=${`Download ${this.configuration}`}
        .type=${"compile"}
        .spawnParams=${{configuration:this.configuration}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        ${void 0===this._result?"":0===this._result?l`
                <mwc-button
                  slot="secondaryAction"
                  label="Download"
                  @click=${this._handleDownload}
                ></mwc-button>
              `:l`
                <mwc-button
                  slot="secondaryAction"
                  dialogAction="close"
                  label="Retry"
                  @click=${this._handleRetry}
                ></mwc-button>
              `}
      </esphome-process-dialog>
    `}_handleProcessDone(o){this._result=o.detail,0===o.detail&&n(this.configuration,this.platformSupportsWebSerial)}_handleDownload(){n(this.configuration,this.platformSupportsWebSerial)}_handleRetry(){c(this.configuration,this.platformSupportsWebSerial)}_handleClose(){this.parentNode.removeChild(this)}};p.styles=[o,t`
      a {
        text-decoration: none;
      }
    `],e([i()],p.prototype,"configuration",void 0),e([i()],p.prototype,"platformSupportsWebSerial",void 0),e([i()],p.prototype,"downloadFactoryFirmware",void 0),e([s()],p.prototype,"_result",void 0),p=e([r("esphome-compile-dialog")],p);
//# sourceMappingURL=c.D3e4Rk27.js.map

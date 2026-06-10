import{B as o,_ as i,e as t,t as s,n as e,s as n,x as a,D as l,o as c}from"./index-zaYCB7m6.js";import"./c.CzGI896K.js";import"./c.B41VBpbv.js";import"./c.Dfz7XRSh.js";let d=class extends n{render(){const o=void 0===this._valid?"":this._valid?"✅":"❌";return a`
      <esphome-process-dialog
        .heading=${`Validate ${this.configuration} ${o}`}
        .type=${"validate"}
        .spawnParams=${{configuration:this.configuration}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Install"
          @click=${this._openInstall}
        ></mwc-button>
      </esphome-process-dialog>
    `}_openEdit(){l(this.configuration)}_openInstall(){c(this.configuration)}_handleProcessDone(o){this._valid=0==o.detail}_handleClose(){this.parentNode.removeChild(this)}};d.styles=[o],i([t()],d.prototype,"configuration",void 0),i([s()],d.prototype,"_valid",void 0),d=i([e("esphome-validate-dialog")],d);
//# sourceMappingURL=c.BiTKbiHp.js.map

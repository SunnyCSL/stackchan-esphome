import{B as o,_ as t,e as i,n as s,s as e,x as n,D as a,o as l}from"./index-zaYCB7m6.js";import"./c.CzGI896K.js";import"./c.B41VBpbv.js";import"./c.Dfz7XRSh.js";let c=class extends e{render(){return n`
      <esphome-process-dialog
        .heading=${`Clean ${this.configuration}`}
        .type=${"clean"}
        .spawnParams=${{configuration:this.configuration}}
        @closed=${this._handleClose}
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
    `}_openEdit(){a(this.configuration)}_openInstall(){l(this.configuration)}_handleClose(){this.parentNode.removeChild(this)}};c.styles=[o],t([i()],c.prototype,"configuration",void 0),c=t([s("esphome-clean-dialog")],c);
//# sourceMappingURL=c.qqsBsE4p.js.map

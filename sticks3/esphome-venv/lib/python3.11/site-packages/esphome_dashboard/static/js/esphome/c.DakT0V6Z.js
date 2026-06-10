import{_ as t,t as e,n as s,s as i,x as o,l as a,r}from"./index-zaYCB7m6.js";import"./c.B41VBpbv.js";let m=class extends i{async showDialog(t,e){this._params=t,this._resolve=e}render(){return this._params?o`
      <mwc-dialog
        .heading=${this._params.title||""}
        @closed=${this._handleClose}
        open
      >
        ${this._params.text?o`<div>${this._params.text}</div>`:""}
        <mwc-button
          slot="secondaryAction"
          no-attention
          .label=${this._params.dismissText||"Cancel"}
          dialogAction="dismiss"
        ></mwc-button>
        <mwc-button
          slot="primaryAction"
          .label=${this._params.confirmText||"Yes"}
          class=${a({destructive:this._params.destructive||!1})}
          dialogAction="confirm"
        ></mwc-button>
      </mwc-dialog>
    `:o``}_handleClose(t){this._resolve("confirm"===t.detail.action),this.parentNode.removeChild(this)}static get styles(){return r`
      mwc-button {
        --mdc-theme-primary: var(--primary-text-color);
      }

      .destructive {
        --mdc-theme-primary: var(--alert-error-color);
      }
    `}};t([e()],m.prototype,"_params",void 0),t([e()],m.prototype,"_resolve",void 0),m=t([s("esphome-confirmation-dialog")],m);
//# sourceMappingURL=c.DakT0V6Z.js.map

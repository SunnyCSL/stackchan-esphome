import{B as t,_ as s,e as o,t as e,i,n as a,s as r,x as l,D as h}from"./index-zaYCB7m6.js";import"./c.CzGI896K.js";import{o as c}from"./c.DjjrZX7w.js";import"./c.B41VBpbv.js";import"./c.Dfz7XRSh.js";import"./c.BsE5xiOP.js";import"./c.JensFMpi.js";const n="esphome-logs-show-states";let d=class extends r{constructor(){super(...arguments),this._showStates=(()=>{try{return"false"!==localStorage.getItem(n)}catch{return!0}})()}render(){return l`
      <esphome-process-dialog
        always-show-close
        ?show-states-toggle=${"OTA"===this.target}
        .showStates=${this._showStates}
        .heading=${`Logs ${this.configuration}`}
        .type=${"logs"}
        .spawnParams=${{configuration:this.configuration,port:this.target,no_states:!this._showStates}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
        @show-states-changed=${this._toggleShowStates}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        ${void 0===this._result||0===this._result?"":l`
              <mwc-button
                slot="secondaryAction"
                dialogAction="close"
                label="Retry"
                @click=${this._handleRetry}
              ></mwc-button>
            `}
      </esphome-process-dialog>
    `}_openEdit(){h(this.configuration)}_handleProcessDone(t){this._result=t.detail}_handleRetry(){c(this.configuration,this.target)}async _toggleShowStates(t){var s,o;this._showStates=t.detail,(t=>{try{localStorage.setItem(n,String(t))}catch{}})(this._showStates),this._result=void 0,await this.updateComplete,await(null===(s=this._processDialog)||void 0===s?void 0:s.updateComplete),null===(o=this._processDialog)||void 0===o||o.restart()}_handleClose(){this.parentNode.removeChild(this)}};d.styles=[t],s([o()],d.prototype,"configuration",void 0),s([o()],d.prototype,"target",void 0),s([e()],d.prototype,"_result",void 0),s([e()],d.prototype,"_showStates",void 0),s([i("esphome-process-dialog")],d.prototype,"_processDialog",void 0),d=s([a("esphome-logs-dialog")],d);
//# sourceMappingURL=c.D-4X8ZeZ.js.map

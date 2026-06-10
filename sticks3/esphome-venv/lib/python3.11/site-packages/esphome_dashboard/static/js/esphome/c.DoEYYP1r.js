import{a as e,b as t,M as i,_ as o,i as r,t as a,e as s,c as d,d as n,h as c,j as l,F as m,R as h,x as p,k as u,l as _,m as b,r as g,n as f,p as v,s as y,o as w,q as k,u as x,v as S,y as $,z as C,A as P,B as E,C as A}from"./index-zaYCB7m6.js";import"./c.B41VBpbv.js";import"./c.Dfz7XRSh.js";import{o as D,c as T}from"./c.Ceriyo_r.js";import{s as B,a as R,b as H,m as I,c as F}from"./c.JensFMpi.js";import{g as N,f as O,r as z}from"./c.B6TNJToz.js";import{S as U,a as L,c as j,s as M}from"./c.fZJwopKZ.js";import{c as W}from"./c.CAJ3Ydmf.js";import{s as q}from"./c.BqFZjOdP.js";const K=Symbol("selection controller");class Y{constructor(){this.selected=null,this.ordered=null,this.set=new Set}}class V{constructor(e){this.sets={},this.focusedSet=null,this.mouseIsDown=!1,this.updating=!1,e.addEventListener("keydown",(e=>{this.keyDownHandler(e)})),e.addEventListener("mousedown",(()=>{this.mousedownHandler()})),e.addEventListener("mouseup",(()=>{this.mouseupHandler()}))}static getController(e){const t=!("global"in e)||"global"in e&&e.global?document:e.getRootNode();let i=t[K];return void 0===i&&(i=new V(t),t[K]=i),i}keyDownHandler(e){const t=e.target;"checked"in t&&this.has(t)&&("ArrowRight"==e.key||"ArrowDown"==e.key?this.selectNext(t):"ArrowLeft"!=e.key&&"ArrowUp"!=e.key||this.selectPrevious(t))}mousedownHandler(){this.mouseIsDown=!0}mouseupHandler(){this.mouseIsDown=!1}has(e){return this.getSet(e.name).set.has(e)}selectPrevious(e){const t=this.getOrdered(e),i=t.indexOf(e),o=t[i-1]||t[t.length-1];return this.select(o),o}selectNext(e){const t=this.getOrdered(e),i=t.indexOf(e),o=t[i+1]||t[0];return this.select(o),o}select(e){e.click()}focus(e){if(this.mouseIsDown)return;const t=this.getSet(e.name),i=this.focusedSet;this.focusedSet=t,i!=t&&t.selected&&t.selected!=e&&t.selected.focus()}isAnySelected(e){const t=this.getSet(e.name);for(const e of t.set)if(e.checked)return!0;return!1}getOrdered(e){const t=this.getSet(e.name);return t.ordered||(t.ordered=Array.from(t.set),t.ordered.sort(((e,t)=>e.compareDocumentPosition(t)==Node.DOCUMENT_POSITION_PRECEDING?1:0))),t.ordered}getSet(e){return this.sets[e]||(this.sets[e]=new Y),this.sets[e]}register(e){const t=e.name||e.getAttribute("name")||"",i=this.getSet(t);i.set.add(e),i.ordered=null}unregister(e){const t=this.getSet(e.name);t.set.delete(e),t.ordered=null,t.selected==e&&(t.selected=null)}update(e){if(this.updating)return;this.updating=!0;const t=this.getSet(e.name);if(e.checked){for(const i of t.set)i!=e&&(i.checked=!1);t.selected=e}if(this.isAnySelected(e))for(const e of t.set){if(void 0===e.formElementTabIndex)break;e.formElementTabIndex=e.checked?0:-1}this.updating=!1}}var G={NATIVE_CONTROL_SELECTOR:".mdc-radio__native-control"},J={DISABLED:"mdc-radio--disabled",ROOT:"mdc-radio"},Q=function(i){function o(e){return i.call(this,t(t({},o.defaultAdapter),e))||this}return e(o,i),Object.defineProperty(o,"cssClasses",{get:function(){return J},enumerable:!1,configurable:!0}),Object.defineProperty(o,"strings",{get:function(){return G},enumerable:!1,configurable:!0}),Object.defineProperty(o,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},setNativeControlDisabled:function(){}}},enumerable:!1,configurable:!0}),o.prototype.setDisabled=function(e){var t=o.cssClasses.DISABLED;this.adapter.setNativeControlDisabled(e),e?this.adapter.addClass(t):this.adapter.removeClass(t)},o}(i);class X extends m{constructor(){super(...arguments),this._checked=!1,this.useStateLayerCustomProperties=!1,this.global=!1,this.disabled=!1,this.value="on",this.name="",this.reducedTouchTarget=!1,this.mdcFoundationClass=Q,this.formElementTabIndex=0,this.focused=!1,this.shouldRenderRipple=!1,this.rippleElement=null,this.rippleHandlers=new h((()=>(this.shouldRenderRipple=!0,this.ripple.then((e=>{this.rippleElement=e})),this.ripple)))}get checked(){return this._checked}set checked(e){var t,i;const o=this._checked;e!==o&&(this._checked=e,this.formElement&&(this.formElement.checked=e),null===(t=this._selectionController)||void 0===t||t.update(this),!1===e&&(null===(i=this.formElement)||void 0===i||i.blur()),this.requestUpdate("checked",o),this.dispatchEvent(new Event("checked",{bubbles:!0,composed:!0})))}_handleUpdatedValue(e){this.formElement.value=e}renderRipple(){return this.shouldRenderRipple?p`<mwc-ripple unbounded accent
        .internalUseStateLayerCustomProperties="${this.useStateLayerCustomProperties}"
        .disabled="${this.disabled}"></mwc-ripple>`:""}get isRippleActive(){var e;return(null===(e=this.rippleElement)||void 0===e?void 0:e.isActive)||!1}connectedCallback(){super.connectedCallback(),this._selectionController=V.getController(this),this._selectionController.register(this),this._selectionController.update(this)}disconnectedCallback(){this._selectionController.unregister(this),this._selectionController=void 0}focus(){this.formElement.focus()}createAdapter(){return Object.assign(Object.assign({},u(this.mdcRoot)),{setNativeControlDisabled:e=>{this.formElement.disabled=e}})}handleFocus(){this.focused=!0,this.handleRippleFocus()}handleClick(){this.formElement.focus()}handleBlur(){this.focused=!1,this.formElement.blur(),this.rippleHandlers.endFocus()}setFormData(e){this.name&&this.checked&&e.append(this.name,this.value)}render(){const e={"mdc-radio--touch":!this.reducedTouchTarget,"mdc-ripple-upgraded--background-focused":this.focused,"mdc-radio--disabled":this.disabled};return p`
      <div class="mdc-radio ${_(e)}">
        <input
          tabindex="${this.formElementTabIndex}"
          class="mdc-radio__native-control"
          type="radio"
          name="${this.name}"
          aria-label="${b(this.ariaLabel)}"
          aria-labelledby="${b(this.ariaLabelledBy)}"
          .checked="${this.checked}"
          .value="${this.value}"
          ?disabled="${this.disabled}"
          @change="${this.changeHandler}"
          @focus="${this.handleFocus}"
          @click="${this.handleClick}"
          @blur="${this.handleBlur}"
          @mousedown="${this.handleRippleMouseDown}"
          @mouseenter="${this.handleRippleMouseEnter}"
          @mouseleave="${this.handleRippleMouseLeave}"
          @touchstart="${this.handleRippleTouchStart}"
          @touchend="${this.handleRippleDeactivate}"
          @touchcancel="${this.handleRippleDeactivate}">
        <div class="mdc-radio__background">
          <div class="mdc-radio__outer-circle"></div>
          <div class="mdc-radio__inner-circle"></div>
        </div>
        ${this.renderRipple()}
      </div>`}handleRippleMouseDown(e){const t=()=>{window.removeEventListener("mouseup",t),this.handleRippleDeactivate()};window.addEventListener("mouseup",t),this.rippleHandlers.startPress(e)}handleRippleTouchStart(e){this.rippleHandlers.startPress(e)}handleRippleDeactivate(){this.rippleHandlers.endPress()}handleRippleMouseEnter(){this.rippleHandlers.startHover()}handleRippleMouseLeave(){this.rippleHandlers.endHover()}handleRippleFocus(){this.rippleHandlers.startFocus()}changeHandler(){this.checked=this.formElement.checked}}o([r(".mdc-radio")],X.prototype,"mdcRoot",void 0),o([r("input")],X.prototype,"formElement",void 0),o([a()],X.prototype,"useStateLayerCustomProperties",void 0),o([s({type:Boolean})],X.prototype,"global",void 0),o([s({type:Boolean,reflect:!0})],X.prototype,"checked",null),o([s({type:Boolean}),d((function(e){this.mdcFoundation.setDisabled(e)}))],X.prototype,"disabled",void 0),o([s({type:String}),d((function(e){this._handleUpdatedValue(e)}))],X.prototype,"value",void 0),o([s({type:String})],X.prototype,"name",void 0),o([s({type:Boolean})],X.prototype,"reducedTouchTarget",void 0),o([s({type:Number})],X.prototype,"formElementTabIndex",void 0),o([a()],X.prototype,"focused",void 0),o([a()],X.prototype,"shouldRenderRipple",void 0),o([n("mwc-ripple")],X.prototype,"ripple",void 0),o([c,s({attribute:"aria-label"})],X.prototype,"ariaLabel",void 0),o([c,s({attribute:"aria-labelledby"})],X.prototype,"ariaLabelledBy",void 0),o([l({passive:!0})],X.prototype,"handleRippleTouchStart",null);const Z=g`.mdc-touch-target-wrapper{display:inline}.mdc-radio{padding:calc((40px - 20px) / 2)}.mdc-radio .mdc-radio__native-control:enabled:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle{border-color:rgba(0, 0, 0, 0.54)}.mdc-radio .mdc-radio__native-control:enabled:checked+.mdc-radio__background .mdc-radio__outer-circle{border-color:#018786;border-color:var(--mdc-theme-secondary, #018786)}.mdc-radio .mdc-radio__native-control:enabled+.mdc-radio__background .mdc-radio__inner-circle{border-color:#018786;border-color:var(--mdc-theme-secondary, #018786)}.mdc-radio [aria-disabled=true] .mdc-radio__native-control:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio .mdc-radio__native-control:disabled:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle{border-color:rgba(0, 0, 0, 0.38)}.mdc-radio [aria-disabled=true] .mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio .mdc-radio__native-control:disabled:checked+.mdc-radio__background .mdc-radio__outer-circle{border-color:rgba(0, 0, 0, 0.38)}.mdc-radio [aria-disabled=true] .mdc-radio__native-control+.mdc-radio__background .mdc-radio__inner-circle,.mdc-radio .mdc-radio__native-control:disabled+.mdc-radio__background .mdc-radio__inner-circle{border-color:rgba(0, 0, 0, 0.38)}.mdc-radio .mdc-radio__background::before{background-color:#018786;background-color:var(--mdc-theme-secondary, #018786)}.mdc-radio .mdc-radio__background::before{top:calc(-1 * (40px - 20px) / 2);left:calc(-1 * (40px - 20px) / 2);width:40px;height:40px}.mdc-radio .mdc-radio__native-control{top:calc((40px - 40px) / 2);right:calc((40px - 40px) / 2);left:calc((40px - 40px) / 2);width:40px;height:40px}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-radio.mdc-radio--disabled [aria-disabled=true] .mdc-radio__native-control:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio.mdc-radio--disabled .mdc-radio__native-control:disabled:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle{border-color:GrayText}.mdc-radio.mdc-radio--disabled [aria-disabled=true] .mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio.mdc-radio--disabled .mdc-radio__native-control:disabled:checked+.mdc-radio__background .mdc-radio__outer-circle{border-color:GrayText}.mdc-radio.mdc-radio--disabled [aria-disabled=true] .mdc-radio__native-control+.mdc-radio__background .mdc-radio__inner-circle,.mdc-radio.mdc-radio--disabled .mdc-radio__native-control:disabled+.mdc-radio__background .mdc-radio__inner-circle{border-color:GrayText}}.mdc-radio{display:inline-block;position:relative;flex:0 0 auto;box-sizing:content-box;width:20px;height:20px;cursor:pointer;will-change:opacity,transform,border-color,color}.mdc-radio__background{display:inline-block;position:relative;box-sizing:border-box;width:20px;height:20px}.mdc-radio__background::before{position:absolute;transform:scale(0, 0);border-radius:50%;opacity:0;pointer-events:none;content:"";transition:opacity 120ms 0ms cubic-bezier(0.4, 0, 0.6, 1),transform 120ms 0ms cubic-bezier(0.4, 0, 0.6, 1)}.mdc-radio__outer-circle{position:absolute;top:0;left:0;box-sizing:border-box;width:100%;height:100%;border-width:2px;border-style:solid;border-radius:50%;transition:border-color 120ms 0ms cubic-bezier(0.4, 0, 0.6, 1)}.mdc-radio__inner-circle{position:absolute;top:0;left:0;box-sizing:border-box;width:100%;height:100%;transform:scale(0, 0);border-width:10px;border-style:solid;border-radius:50%;transition:transform 120ms 0ms cubic-bezier(0.4, 0, 0.6, 1),border-color 120ms 0ms cubic-bezier(0.4, 0, 0.6, 1)}.mdc-radio__native-control{position:absolute;margin:0;padding:0;opacity:0;cursor:inherit;z-index:1}.mdc-radio--touch{margin-top:4px;margin-bottom:4px;margin-right:4px;margin-left:4px}.mdc-radio--touch .mdc-radio__native-control{top:calc((40px - 48px) / 2);right:calc((40px - 48px) / 2);left:calc((40px - 48px) / 2);width:48px;height:48px}.mdc-radio.mdc-ripple-upgraded--background-focused .mdc-radio__focus-ring,.mdc-radio:not(.mdc-ripple-upgraded):focus .mdc-radio__focus-ring{pointer-events:none;border:2px solid transparent;border-radius:6px;box-sizing:content-box;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);height:100%;width:100%}@media screen and (forced-colors: active){.mdc-radio.mdc-ripple-upgraded--background-focused .mdc-radio__focus-ring,.mdc-radio:not(.mdc-ripple-upgraded):focus .mdc-radio__focus-ring{border-color:CanvasText}}.mdc-radio.mdc-ripple-upgraded--background-focused .mdc-radio__focus-ring::after,.mdc-radio:not(.mdc-ripple-upgraded):focus .mdc-radio__focus-ring::after{content:"";border:2px solid transparent;border-radius:8px;display:block;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);height:calc(100% + 4px);width:calc(100% + 4px)}@media screen and (forced-colors: active){.mdc-radio.mdc-ripple-upgraded--background-focused .mdc-radio__focus-ring::after,.mdc-radio:not(.mdc-ripple-upgraded):focus .mdc-radio__focus-ring::after{border-color:CanvasText}}.mdc-radio__native-control:checked+.mdc-radio__background,.mdc-radio__native-control:disabled+.mdc-radio__background{transition:opacity 120ms 0ms cubic-bezier(0, 0, 0.2, 1),transform 120ms 0ms cubic-bezier(0, 0, 0.2, 1)}.mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio__native-control:disabled+.mdc-radio__background .mdc-radio__outer-circle{transition:border-color 120ms 0ms cubic-bezier(0, 0, 0.2, 1)}.mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__inner-circle,.mdc-radio__native-control:disabled+.mdc-radio__background .mdc-radio__inner-circle{transition:transform 120ms 0ms cubic-bezier(0, 0, 0.2, 1),border-color 120ms 0ms cubic-bezier(0, 0, 0.2, 1)}.mdc-radio--disabled{cursor:default;pointer-events:none}.mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__inner-circle{transform:scale(0.5);transition:transform 120ms 0ms cubic-bezier(0, 0, 0.2, 1),border-color 120ms 0ms cubic-bezier(0, 0, 0.2, 1)}.mdc-radio__native-control:disabled+.mdc-radio__background,[aria-disabled=true] .mdc-radio__native-control+.mdc-radio__background{cursor:default}.mdc-radio__native-control:focus+.mdc-radio__background::before{transform:scale(1);opacity:.12;transition:opacity 120ms 0ms cubic-bezier(0, 0, 0.2, 1),transform 120ms 0ms cubic-bezier(0, 0, 0.2, 1)}:host{display:inline-block;outline:none}.mdc-radio{vertical-align:bottom}.mdc-radio .mdc-radio__native-control:enabled:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle{border-color:var(--mdc-radio-unchecked-color, rgba(0, 0, 0, 0.54))}.mdc-radio [aria-disabled=true] .mdc-radio__native-control:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio .mdc-radio__native-control:disabled:not(:checked)+.mdc-radio__background .mdc-radio__outer-circle{border-color:var(--mdc-radio-disabled-color, rgba(0, 0, 0, 0.38))}.mdc-radio [aria-disabled=true] .mdc-radio__native-control:checked+.mdc-radio__background .mdc-radio__outer-circle,.mdc-radio .mdc-radio__native-control:disabled:checked+.mdc-radio__background .mdc-radio__outer-circle{border-color:var(--mdc-radio-disabled-color, rgba(0, 0, 0, 0.38))}.mdc-radio [aria-disabled=true] .mdc-radio__native-control+.mdc-radio__background .mdc-radio__inner-circle,.mdc-radio .mdc-radio__native-control:disabled+.mdc-radio__background .mdc-radio__inner-circle{border-color:var(--mdc-radio-disabled-color, rgba(0, 0, 0, 0.38))}`;let ee=class extends X{};ee.styles=[Z],ee=o([f("mwc-radio")],ee);let te=class extends y{constructor(){super(...arguments),this._busy=!1,this._platform="ESP32",this._board=this._platformData().defaultBoard,this._useRecommended=!0,this._hasWifiSecrets=void 0,this._data={type:"basic",ssid:`!secret ${L}`,psk:`!secret ${U}`},this._state=B?"pick_new_config_type":"ask_esphome_web",this._installed=!1,this._isDraggingOverConfigUpload=!1,this._cleanSSIDBlur=e=>{const t=e.target;t.value=t.value.trim()}}_platformData(){return R[this._platform]}render(){let e,t,i=!1;return"ask_esphome_web"===this._state?[e,t,i]=this._renderAskESPHomeWeb():"pick_new_config_type"===this._state?[e,t,i]=this._renderPickNewConfigType():"basic_config"===this._state?[e,t,i]=this._renderBasicConfig():"empty_config"===this._state?[e,t,i]=this._renderEmptyConfig():"pick_platform"===this._state?(e="Select your device type",t=this._renderPickPlatform()):"pick_board"===this._state?(e=this._platformData().showInPickerTitle?`Select your ${this._platformData().label} board`:"Select your board",t=this._renderPickBoard()):"connect_webserial"===this._state?(e="Installation",t=this._renderConnectSerial()):"connecting_webserial"===this._state?(t=this._renderProgress("Connecting"),i=!0):"prepare_flash"===this._state?(t=this._renderProgress("Preparing installation"),i=!0):"flashing"===this._state?(t=void 0===this._writeProgress?this._renderProgress("Erasing"):this._renderProgress(p`
                Installing<br /><br />
                This will take
                ${"ESP8266"===this._platform?"a minute":"2 minutes"}.<br />
                Keep this page visible to prevent slow down
              `,this._writeProgress>3?this._writeProgress:void 0),i=!0):"wait_come_online"===this._state?(t=this._renderProgress("Finding device on network"),i=!0):"done"===this._state&&(t=this._renderDone()),p`
      <mwc-dialog
        open
        heading=${e}
        scrimClickAction
        @closed=${this._handleClose}
        .hideActions=${i}
        >${t}</mwc-dialog
      >
    `}_renderProgress(e,t){return p`
      <div class="center">
        <div>
          <mwc-circular-progress
            active
            ?indeterminate=${void 0===t}
            .progress=${void 0!==t?t/100:void 0}
            density="8"
          ></mwc-circular-progress>
          ${void 0!==t?p`<div class="progress-pct">${t}%</div>`:""}
        </div>
        ${e}
      </div>
    `}_renderMessage(e,t,i){return p`
      <div class="center">
        <div class="icon">${e}</div>
        ${t}
      </div>
      ${i?p`
            <mwc-button
              slot="primaryAction"
              dialogAction="ok"
              label="Close"
            ></mwc-button>
          `:""}
    `}_renderAskESPHomeWeb(){return["New device",p`
      <div>
        A device needs to be connected to a computer using a USB cable to be
        added to ESPHome. Once added, ESPHome will interact with the device
        wirelessly.
      </div>
      <div>
        ${H?"Your browser does not support WebSerial.":"You are not browsing the ESPHome Device Builder over a secure connection (HTTPS)."}
        This prevents ESPHome from being able to install this on devices
        connected to this computer.
      </div>
      <div>
        You will still be able to install ESPHome by connecting the device to
        the computer that runs the ESPHome Device Builder.
      </div>
      <div>
        Alternatively, you can use ESPHome Web to prepare a device for being
        used with ESPHome using this computer.
      </div>

      <mwc-button
        slot="primaryAction"
        label="Continue"
        @click=${()=>{this._state="pick_new_config_type"}}
      ></mwc-button>

      <a
        slot="secondaryAction"
        href=${"https://web.esphome.io/?dashboard_wizard"}
        target="_blank"
        rel="noopener"
      >
        <mwc-button
          no-attention
          dialogAction="close"
          label="Open ESPHome Web"
        ></mwc-button>
      </a>
    `,!1]}_renderPickNewConfigType(){return["Create configuration",p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}
      <div
        @dragover=${e=>{e.preventDefault(),this._isDraggingOverConfigUpload=!0}}
        @dragleave=${e=>{e.preventDefault(),this._isDraggingOverConfigUpload=!1}}
        @drop=${e=>{var t,i;e.preventDefault(),this._isDraggingOverConfigUpload=!1;const o=null===(i=null===(t=e.dataTransfer)||void 0===t?void 0:t.files)||void 0===i?void 0:i[0];if(o){if(!o.name.endsWith(".yaml")&&!o.name.endsWith(".yml"))return void console.error("Invalid file type. Please provide a .yaml or .yml file.");this._configFileInput.files=e.dataTransfer.files,this._handleConfigFileUpload()}}}
        class="${_({"dragging-over":this._isDraggingOverConfigUpload})}"
      >
        <input
          type="file"
          accept=".yaml,.yml"
          style="display: none;"
          id="config-file-input"
          @change=${this._handleConfigFileUpload}
        />
        <p>How would you like to create your configuration?</p>
        <mwc-list>
          <mwc-list-item
            twoline
            hasMeta
            @click=${()=>{this._state="basic_config"}}
          >
            <span>New Device Setup</span>
            <span slot="secondary">A guided process to get you started.</span>
            ${I}
          </mwc-list-item>
          <mwc-list-item
            twoline
            hasMeta
            @click=${()=>{this._configFileInput.click()}}
          >
            <span>Import from File</span>
            <span slot="secondary"
              >Use an existing ESPHome configuration (.yaml).</span
            >
            ${I}
          </mwc-list-item>
          <mwc-list-item
            twoline
            hasMeta
            @click=${()=>{this._state="empty_config"}}
          >
            <span>Empty Configuration</span>
            <span slot="secondary"
              >For manually writing or pasting a configuration.</span
            >
            ${I}
          </mwc-list-item>
        </mwc-list>
        <small>You can also drag and drop your .yaml file here</small>
      </div>
    `,!0]}_renderBasicConfig(){if(void 0===this._hasWifiSecrets)return[void 0,this._renderProgress("Initializing"),!0];return[B?"New device":"Create configuration",p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}

      <mwc-textfield label="Name" name="name" required></mwc-textfield>

      ${this._hasWifiSecrets?p`
            <div>
              This device will be configured to connect to the Wi-Fi network
              stored in your secrets.
            </div>
          `:p`
            <div>
              Enter the credentials of the Wi-Fi network that you want your
              device to connect to.
            </div>
            <div>
              This information will be stored in your secrets and used for this
              and future devices. You can edit the information later by editing
              your secrets at the top of the page.
            </div>

            <mwc-textfield
              label="Network name"
              name="ssid"
              required
              @blur=${this._cleanSSIDBlur}
            ></mwc-textfield>

            <mwc-textfield
              label="Password"
              name="password"
              type="password"
              helper="Leave blank if no password"
            ></mwc-textfield>
          `}

      <mwc-button
        slot="primaryAction"
        label="Next"
        @click=${this._handleBasicConfigSubmit}
      ></mwc-button>

      <mwc-button
        no-attention
        slot="secondaryAction"
        dialogAction="close"
        label="Cancel"
      ></mwc-button>
    `,!1]}_renderEmptyConfig(){this._data.type="empty";return["Create empty configuration",p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}

      <mwc-textfield label="Name" name="name" required></mwc-textfield>

      <mwc-button
        slot="primaryAction"
        label="Next"
        @click=${this._handleEmptyConfigSubmit}
      ></mwc-button>

      <mwc-button
        no-attention
        slot="secondaryAction"
        dialogAction="close"
        label="Cancel"
      ></mwc-button>
    `,!1]}_renderPickPlatform(){return p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}

      <div>
        Select the type of device that this configuration will be installed on.
      </div>

      <mwc-list class="platforms">
        ${Object.keys(R).map((e=>R[e].showInDeviceTypePicker?p`
                  <mwc-list-item
                    hasMeta
                    .platform=${e}
                    @click=${this._handlePickPlatformClick}
                  >
                    <span>${R[e].label}</span>
                    ${I}
                  </mwc-list-item>
                `:p``))}
      </mwc-list>

      <mwc-formfield class="footer-left" label="Use recommended settings">
        <mwc-checkbox
          name="use-recommended"
          @change=${this._handleUseRecommendedCheckbox}
          ?checked=${this._useRecommended}
        ></mwc-checkbox>
      </mwc-formfield>

      <mwc-button
        no-attention
        slot="primaryAction"
        dialogAction="close"
        label="Cancel"
      ></mwc-button>
    `}_renderPickBoard(){const e=this._platformData().defaultBoard;let t=null;if(e&&this._supportedBoards)for(let i of this._supportedBoards)if(e in i.items){t=i.items[e];break}return p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}
      ${this._supportedBoards?p`
            <select
              @change=${this._handlePickBoardSelect}
              size="15"
              style="width: 100%;"
            >
              ${e&&t?p`<option value="${e}" selected>
                      ${t} (default)
                    </option>
                    <option disabled>------</option>`:""}
              ${this._supportedBoards.map((t=>{const i=Object.keys(t.items).map((i=>i===e?p``:p`<option value="${i}">${t.items[i]}</option>`));return t.title?p`<optgroup label="${t.title}">${i}</optgroup>`:i}))}
            </select>
          `:p`<div>Loading board list...</div>`}

      <mwc-button
        slot="primaryAction"
        label="Next"
        @click=${this._handlePickBoardSubmit}
        ?disabled=${null===this._board}
      ></mwc-button>
      <mwc-button
        no-attention
        slot="secondaryAction"
        label="Back"
        @click=${()=>this._state="pick_platform"}
      ></mwc-button>
    `}_renderConnectSerial(){return p`
      ${this._error?p`<div class="error">${this._error}</div>`:""}

      <div>
        ESPHome will now create your configuration and install it on your
        device.
      </div>

      <div>
        Connect your ESP8266 or ESP32 with a USB cable to your computer and
        click on connect. You need to do this once. Later updates install
        wirelessly.
        <a
          href="https://esphome.io/guides/getting_started_hassio.html#webserial"
          target="_blank"
          >Learn more</a
        >
      </div>

      <div>
        Skip this step to install it on your device later or if you are using a
        Raspberry Pi Pico.
      </div>

      <mwc-button
        slot="primaryAction"
        label="Connect"
        .disabled=${this._busy}
        @click=${this._handleConnectSerialSubmit}
      ></mwc-button>
      <mwc-button
        no-attention
        slot="secondaryAction"
        label="Skip this step"
        .disabled=${this._busy}
        @click=${this._handleConnectSerialSkip}
      ></mwc-button>
    `}_renderDone(){return this._error?this._renderMessage("👀",this._error,!0):p`
      ${this._renderMessage("🎉","Configuration created!",!1)}
      ${this._installed?"":p`
            <div>
              You can now install the configuration to your device. The first
              time this requires a cable.
            </div>
            <div>
              Once the device is installed and connected to your network, you
              will be able to manage it wirelessly.
            </div>
          `}
      ${this._apiKey?p`
            <p>
              Each ESPHome device has a unique encryption key to talk to other
              devices. You will need this key to include your device in Home
              Assistant. You can find the key later in the device menu.
            </p>
            <div class="api-key-container">
              <mwc-textfield
                label="Encryption key"
                readonly
                name="api_key"
                value=${this._apiKey}
                @click=${this._handleCopyApiKey}
              ></mwc-textfield>
              <div class="api-key-banner">Copied!</div>
            </div>
          `:""}
      ${this._installed?p`
            <mwc-button
              slot="primaryAction"
              dialogAction="ok"
              label="Close"
            ></mwc-button>
          `:p`
            <mwc-button
              slot="primaryAction"
              dialogAction="ok"
              label="Install"
              @click=${()=>w(this._configFilename)}
            ></mwc-button>
            <mwc-button
              no-attention
              slot="secondaryAction"
              dialogAction="close"
              label="Skip"
            ></mwc-button>
          `}
    `}firstUpdated(e){super.firstUpdated(e),j().then((e=>{this._hasWifiSecrets=e}))}updated(e){if(super.updated(e),e.has("_state")||e.has("_hasWifiSecrets")){const e=this.shadowRoot.querySelector("mwc-textfield, mwc-radio, mwc-button");e&&e.updateComplete.then((()=>e.focus()))}if("pick_board"==this._state){if(e.has("_state")){(e=>v(`./boards/${e}`))(this._platform.toLowerCase()).then((e=>{this._supportedBoards=e,this._busy=!1}))}if(e.has("_busy")&&!this._busy){const e=this.shadowRoot.querySelector("select");e&&e.focus()}}}async _handleBasicConfigSubmit(){const e=this._inputName,t=e.reportValidity(),i=!!this._hasWifiSecrets||this._inputSSID.reportValidity();if(!t)return void e.focus();if(!i)return void this._inputSSID.focus();const o=e.value;this._data.name=o,this._hasWifiSecrets||(this._wifi={ssid:this._inputSSID.value,password:this._inputPassword.value}),setTimeout((()=>{this._state=B&&H?"connect_webserial":"pick_platform"}),0)}async _handleEmptyConfigSubmit(){const e=this._inputName;if(e.reportValidity()){this._busy=!0,this._data.type="empty",this._data.name=e.value;try{const e=await k(this._data);this._configFilename=e.configuration,x(),this._dialog.close()}catch(e){this._error=e.message||e}finally{this._busy=!1}}else e.focus()}_encodeToBase64(e){const t=(new TextEncoder).encode(e);let i="";for(let e=0;e<t.length;e++)i+=String.fromCharCode(t[e]);return btoa(i)}async _handleConfigFileUpload(){var e;const t=null===(e=this._configFileInput.files)||void 0===e?void 0:e[0];try{const e=await k({type:"upload",name:null==t?void 0:t.name.replace(/\.ya?ml$/,""),file_content:this._encodeToBase64(t?await t.text():"")});this._configFilename=e.configuration,x(),this._state="done"}catch(e){console.error("err was",e.message),this._error=e.message||e}finally{this._busy=!1}}_handleUseRecommendedCheckbox(e){this._useRecommended=e.target.checked}_handlePickBoardSelect(e){this._board=e.target.value}async _handlePickPlatformClick(e){this._supportedBoards=void 0,this._platform=e.currentTarget.platform,this._board=this._platformData().defaultBoard,this._useRecommended&&null!==this._board?await this._handlePickBoardSubmit():(this._busy=!0,this._state="pick_board")}async _handlePickBoardSubmit(){if(this._board&&"basic"===this._data.type){this._data.board=this._board,this._busy=!0;try{this._wifi&&await M(this._wifi.ssid,this._wifi.password);const e=await k(this._data);this._configFilename=e.configuration,x(),this._apiKey=await S(this._configFilename),this._state="done"}catch(e){this._error=e.message||e}finally{this._busy=!1}}}_handleConnectSerialSkip(){this._error=void 0,this._state="pick_platform"}async _handleConnectSerialSubmit(){var e;let t;this._busy=!0,this._error=void 0;let i=!1;if("basic"===this._data.type)try{let o,r;try{o=await navigator.serial.requestPort()}catch(e){return console.error(e),void("NotFoundError"===e.name?D():this._error=e.message||String(e))}t=T(o),this._state="connecting_webserial";try{await t.main(),await t.flashId()}catch(e){return console.error(e),this._state="connect_webserial",void(this._error="Failed to initialize. Try resetting your device or holding the BOOT button while selecting your serial port until it starts preparing the installation.")}this._state="prepare_flash";const a=t.chip.CHIP_NAME;if(!(a in F))return this._state="connect_webserial",void(this._error=`Unable to identify the connected device (${t.chip.CHIP_NAME}).`);r=F[a],this._data.board=null!==(e=R[r].defaultBoard)&&void 0!==e?e:void 0;try{const{configuration:e}=await k(this._data);this._configFilename=e}catch(e){return console.error(e),this._state="connect_webserial",void(this._error="Unable to create the configuration")}i=!0;try{await $(this._configFilename)}catch(e){return console.error(e),this._state="connect_webserial",void(this._error="Unable to compile the configuration")}this._state="flashing";try{const e=await N(this._configFilename);await O(t,e,!0,(e=>{this._writeProgress=e}))}catch(e){return console.error(e),this._state="connect_webserial",void(this._error="Error installing the configuration")}i=!1,this._installed=!0,await z(t.transport),this._state="wait_come_online";try{await new Promise(((e,t)=>{const i=C((t=>{t[this._configFilename]&&(i(),clearTimeout(o),e(void 0))})),o=setTimeout((()=>{i(),t("Timeout")}),2e4)}))}catch(e){console.error(e),this._error="Configuration created but unable to detect the device on the network"}this._state="done"}finally{this._busy=!1,t&&(console.log("Closing port"),await t.transport.disconnect()),i&&await P(this._configFilename)}}async _handleClose(){this.parentNode.removeChild(this)}async _handleCopyApiKey(){var e;W(this._apiKey),this._inputApiKeyBanner.style.setProperty("display","flex"),await q(3e3),null===(e=this._inputApiKeyBanner)||void 0===e||e.style.setProperty("display","none")}};te.styles=[E,A,g`
      :host {
        --mdc-dialog-max-width: 490px;
      }
      .center {
        text-align: center;
      }
      mwc-circular-progress {
        margin-bottom: 16px;
      }
      .progress-pct {
        position: absolute;
        top: 50px;
        left: 0;
        right: 0;
      }
      .icon {
        font-size: 50px;
        line-height: 80px;
        color: black;
      }
      .error {
        color: var(--alert-error-color);
        margin-bottom: 16px;
      }
      .api-key-container {
        position: relative;
      }
      .api-key-banner {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--mdc-theme-primary);
        color: white;
        display: none;
        align-items: center;
        justify-content: center;
        margin: 0 !important;
        font-weight: bold;
        border-radius: 2px;
      }
      .footer-left {
        position: absolute;
        left: 0;
        bottom: 4px;
        z-index: 1;
      }
      .dragging-over {
        outline: 2px dashed var(--mdc-theme-primary);
        background-color: rgba(0, 0, 0, 0.05);
      }
    `],o([a()],te.prototype,"_busy",void 0),o([a()],te.prototype,"_board",void 0),o([a()],te.prototype,"_useRecommended",void 0),o([a()],te.prototype,"_hasWifiSecrets",void 0),o([a()],te.prototype,"_writeProgress",void 0),o([a()],te.prototype,"_state",void 0),o([a()],te.prototype,"_error",void 0),o([r("mwc-textfield[name=name]")],te.prototype,"_inputName",void 0),o([r("mwc-textfield[name=ssid]")],te.prototype,"_inputSSID",void 0),o([r("mwc-textfield[name=password]")],te.prototype,"_inputPassword",void 0),o([r(".api-key-banner")],te.prototype,"_inputApiKeyBanner",void 0),o([r("mwc-dialog")],te.prototype,"_dialog",void 0),o([a()],te.prototype,"_isDraggingOverConfigUpload",void 0),o([r("#config-file-input")],te.prototype,"_configFileInput",void 0),te=o([f("esphome-wizard-dialog")],te);export{te as ESPHomeWizardDialog};
//# sourceMappingURL=c.DoEYYP1r.js.map

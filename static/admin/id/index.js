"use strict";

require("core-js/modules/es.weak-map.js");
require("core-js/modules/web.dom-collections.iterator.js");
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Widget = exports.Control = void 0;
require("core-js/modules/es.string.trim.js");
var _react = _interopRequireWildcard(require("react"));
var _shortid = _interopRequireDefault(require("shortid"));
var _propTypes = _interopRequireDefault(require("prop-types"));
function _interopRequireDefault(e) { return e && e.__esModule ? e : { default: e }; }
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { default: e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && {}.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n.default = e, t && t.set(e, n), n; }
const wrapper = {
  display: 'flex',
  justifyContent: 'space-between',
  width: '100%',
  padding: '16px 20px',
  margin: '0px',
  border: '2px solid rgb(223, 223, 227)',
  borderRadius: '0px 5px 5px',
  outline: '0px',
  boxShadow: 'none',
  backgroundColor: 'rgb(255, 255, 255)',
  color: 'rgb(205, 205, 205)',
  transition: 'border-color 0.2s ease 0s',
  position: 'relative',
  fontSize: '15px'
};
const button = {
  marginLeft: '1em',
  display: 'block',
  border: '0px',
  cursor: 'pointer',
  height: '27px',
  lineHeight: '27px',
  fontSize: '12px',
  fontWeight: 600,
  borderRadius: '3px',
  padding: '0px 14px',
  backgroundColor: 'rgb(121, 130, 145)',
  color: 'rgb(255, 255, 255)',
  marginRight: '8px'
};
const Control = _ref => {
  let {
    field,
    forID,
    value,
    onChange: _onChange
  } = _ref;
  (0, _react.useEffect)(() => {
    if (!value) {
      _onChange(generateId());
    }
  }, []);
  const generateId = () => {
    const usePrefix = field.get('prefix');
    const prefix = usePrefix ? usePrefix + '-' : '';
    return prefix + (0, _shortid.default)();
  };
  return /*#__PURE__*/_react.default.createElement("div", {
    style: wrapper
  }, /*#__PURE__*/_react.default.createElement("input", {
    type: "hidden",
    id: forID,
    value: value,
    onChange: e => _onChange(e.target.value.trim())
  }), /*#__PURE__*/_react.default.createElement("span", {
    style: {
      lineHeight: '1.6em'
    }
  }, value || generateId()), /*#__PURE__*/_react.default.createElement("button", {
    onClick: () => {
      _onChange(generateId());
    },
    style: button
  }, "Regenerate ID"));
};
exports.Control = Control;
Control.propTypes = {
  onChange: _propTypes.default.func.isRequired,
  forID: _propTypes.default.string,
  value: _propTypes.default.node,
  classNameWrapper: _propTypes.default.string.isRequired
};
Control.defaultProps = {
  value: ''
};
const Widget = exports.Widget = {
  // name that will be used in config.yml
  name: 'uuid',
  controlComponent: Control
};
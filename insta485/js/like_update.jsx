import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment";

function LikeUnlike({ numlikes, lognameLikesThis, clickFunction }) {
    return (
      <button onClick={clickFunction}>
        Clicked {1} times
      </button>
    );
  }

export default LikeUnlike;
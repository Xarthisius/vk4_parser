meta:
  id: vk4
  file-extension: "vk4"
  endian: le

seq:
  - id: header
    type: header
    size: 12
  - id: offset_table
    type: offset_table
    size: 72
  - id: meas_conds
    type: measurement_conditions

instances:
  assembly_header:
    pos: offset_table.assemble
    type: assembly_header
  color_peak:
    pos: offset_table.color_peak
    type: true_color_image
  color_light:
    pos: offset_table.color_light
    type: true_color_image
  light:
    repeat: expr
    repeat-expr: offset_table.light.size
    type:
      switch-on: offset_table.light[_index] > 0
      cases:
        true: data_image(offset_table.light[_index])
        false: blank
  height:
    repeat: expr
    repeat-expr: offset_table.height.size
    type:
      switch-on: offset_table.height[_index] > 0
      cases:
        true: data_image(offset_table.height[_index])
        false: blank
  color_peak_thumbnail:
    pos: offset_table.color_peak_thumbnail
    type: true_color_image
  color_light_thumbnail:
    pos: offset_table.color_light_thumbnail
    type: true_color_image
  light_thumbnail:
    pos: offset_table.light_thumbnail
    type: true_color_image
  height_thumbnail:
    pos: offset_table.height_thumbnail
    type: true_color_image
  strings:
    pos: offset_table.string_data
    type: coded_string
    repeat: expr
    repeat-expr: 2

types:
  blank:
    seq: []
  data_image:
    params:
      - id: root_pos
        type: u8
    instances:
      value:
        pos: root_pos
        type: false_color_image
  header:
    seq:
      - id: magic
        contents: [86, 75, 52, 95]    
      - id: dll_version
        size: 4
      - id: file_type
        size: 4
  offset_table:
    seq:
      - id: setting
        type: u4
      - id: color_peak
        type: u4
      - id: color_light
        type: u4
      - id: light
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: height
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: color_peak_thumbnail
        type: u4
      - id: color_light_thumbnail
        type: u4
      - id: light_thumbnail
        type: u4
      - id: height_thumbnail
        type: u4
      - id: assemble
        type: u4
      - id: line_measure
        type: u4
      - id: line_thickness
        type: u4
      - id: string_data
        type: u4
      - id: reserved
        type: u4
  measurement_conditions:
    seq:
      - id: struct_size
        type: u4
        valid:
          min: 304
      - id: conditions
        type: measurement_condition
        size: struct_size - 4
  measurement_condition:
    seq:
      - id: year
        type: u4
      - id: month
        type: u4
      - id: day
        type: u4
      - id: hour
        type: u4
      - id: minute
        type: u4
      - id: second
        type: u4
      - id: diff_utc_by_minutes
        type: s4
      - id: image_attributes
        type: u4
      - id: user_interface_mode
        type: u4
      - id: color_composite_mode
        type: u4
      - id: num_layer
        type: u4
      - id: run_mode
        type: u4
      - id: peak_mode
        type: u4
      - id: sharpening_level
        type: u4
      - id: speed
        type: u4
      - id: distance
        type: u4
      - id: pitch
        type: u4
      - id: optical_zoom
        type: u4
      - id: num_line
        type: u4
      - id: line0_pos
        type: u4
      - id: reserved1
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: lens_mag
        type: u4
      - id: pmt_gain_mode
        type: u4
      - id: pmt_gain
        type: u4
      - id: pmt_offset
        type: u4
      - id: nd_filter
        type: u4
      - id: reserved2
        type: u4
      - id: persist_count
        type: u4
      - id: shutter_speed_mode
        type: u4
      - id: shutter_speed
        type: u4
      - id: white_balance_mode
        type: u4
      - id: white_balance_red
        type: u4
      - id: white_balance_blue
        type: u4
      - id: camera_gain
        type: u4
      - id: plane_compensation
        type: u4
      - id: xy_length_unit
        type: u4
      - id: z_length_unit
        type: u4
      - id: xy_decimal_place
        type: u4
      - id: z_decimal_place
        type: u4
      - id: x_length_per_pixel
        type: u4
      - id: y_length_per_pixel
        type: u4
      - id: z_length_per_digit
        type: u4
      - id: reserved3
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: light_filter_type
        type: u4
      - id: reserved4
        type: u4
      - id: gamma_reverse
        type: u4
      - id: gamma
        type: u4
      - id: gamma_offset
        type: u4
      - id: ccd_bw_offset
        type: u4
      - id: numerical_aperture
        type: u4
      - id: head_type
        type: u4
      - id: pmt_gain2
        type: u4
      - id: omit_color_image
        type: u4
      - id: lens_id
        type: u4
      - id: light_lut_mode
        type: u4
      - id: light_lut_in0
        type: u4
      - id: light_lut_out0
        type: u4
      - id: light_lut_in1
        type: u4
      - id: light_lut_out1
        type: u4
      - id: light_lut_in2
        type: u4
      - id: light_lut_out2
        type: u4
      - id: light_lut_in3
        type: u4
      - id: light_lut_out3
        type: u4
      - id: light_lut_in4
        type: u4
      - id: light_lut_out4
        type: u4
      - id: upper_position
        type: u4
      - id: lower_position
        type: u4
      - id: light_effective_bit_depth
        type: u4
      - id: height_effective_bit_depth
        type: u4
      - id: remainder
        size-eos: true
  assembly_header:
    seq:
      - id: size
        type: u4
      - id: file_type
        type: u2
        valid:
          any-of: [0, 1, 2]
      - id: stage_type
        type: u2
      - id: x_position
        type: u4
      - id: y_position
        type: u4
      - id: auto_adjustement
        size: 1
      - id: source
        size: 1
      - id: thin_out
        type: u2
      - id: count_x
        type: u2
      - id: count_y
        type: u2
  false_color_image:
    seq:
      - id: width
        type: u4
      - id: height
        type: u4
      - id: bit_depth
        type: u4
        valid:
          any-of: [8, 16, 32]
      - id: compression
        type: u4
      - id: byte_size
        type: u4
      - id: palette_range_min
        type: u4
      - id: palette_range_max
        type: u4
      - id: palette
        type: rgb_record
        repeat: expr
        repeat-expr: 256
      - id: data
        size: width * height * bit_depth / 8
    instances:
      bps:
        value: bit_depth >> 3
  true_color_image:
    seq:
      - id: width
        type: u4
      - id: height
        type: u4
      - id: bit_depth
        type: u4
        valid:
          any-of: [24]
      - id: compression
        type: u4
      - id: byte_size
        type: u4
      ## This is fancy, but extremely slow and memory hungry
      #- id: data
      #  type: rgb_record
      #  repeat: expr
      #  repeat-expr: width * height * bit_depth / 8
      ## Let's read it as a block and do the magic in Python 
      - id: data
        size: width * height * bit_depth / 8
    instances:
      bps:
        value: bit_depth >> 3
  coded_string:
    seq:
      - id: length
        type: u4
      - id: string
        type: str
        size: length * 2
        encoding: UTF-16LE
  rgb_record:
    seq:
      - id: red
        type: u1
      - id: green
        type: u1
      - id: blue
        type: u1

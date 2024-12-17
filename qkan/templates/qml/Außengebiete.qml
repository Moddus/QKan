<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingHints="1" minScale="0" simplifyAlgorithm="0" simplifyMaxScale="1" symbologyReferenceScale="-1" simplifyLocal="1" labelsEnabled="0" simplifyDrawingTol="1" styleCategories="LayerConfiguration|Symbology|Labeling|Fields|Forms|Actions|MapTips|AttributeTable|Rendering|CustomProperties|Notes" readOnly="0" maxScale="0" version="3.22.16-Białowieża" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <renderer-v2 type="singleSymbol" forceraster="0" symbollevels="0" referencescale="-1" enableorderby="0">
    <symbols>
      <symbol type="fill" force_rhr="0" clip_to_extent="1" name="0" alpha="1">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" type="QString" name="name"/>
            <Option name="properties"/>
            <Option value="collection" type="QString" name="type"/>
          </Option>
        </data_defined_properties>
        <layer enabled="1" class="SimpleFill" pass="0" locked="0">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" type="QString" name="border_width_map_unit_scale"/>
            <Option value="225,89,137,255" type="QString" name="color"/>
            <Option value="bevel" type="QString" name="joinstyle"/>
            <Option value="0,0" type="QString" name="offset"/>
            <Option value="3x:0,0,0,0,0,0" type="QString" name="offset_map_unit_scale"/>
            <Option value="MM" type="QString" name="offset_unit"/>
            <Option value="35,35,35,255" type="QString" name="outline_color"/>
            <Option value="solid" type="QString" name="outline_style"/>
            <Option value="0.26" type="QString" name="outline_width"/>
            <Option value="MM" type="QString" name="outline_width_unit"/>
            <Option value="solid" type="QString" name="style"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="225,89,137,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <Option type="Map">
      <Option value="0" type="int" name="embeddedWidgets/count"/>
      <Option type="invalid" name="variableNames"/>
      <Option type="invalid" name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <fieldConfiguration>
    <field configurationFlags="None" name="pk">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="gebnam">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="schnam">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="AllowMulti"/>
            <Option value="false" type="bool" name="AllowNull"/>
            <Option value="" type="QString" name="Description"/>
            <Option value="" type="QString" name="FilterExpression"/>
            <Option value="schnam" type="QString" name="Key"/>
            <Option value="schaechte20161220162259105" type="QString" name="Layer"/>
            <Option value="Schächte" type="QString" name="LayerName"/>
            <Option value="spatialite" type="QString" name="LayerProviderName"/>
            <Option value="dbname='itwh.sqlite' table=&quot;schaechte&quot; (geop) sql=schachttyp = 'Schacht'" type="QString" name="LayerSource"/>
            <Option value="1" type="int" name="NofColumns"/>
            <Option value="false" type="bool" name="OrderByValue"/>
            <Option value="false" type="bool" name="UseCompleter"/>
            <Option value="schnam" type="QString" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="hoeheob">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="hoeheun">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="fliessweg">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="basisabfluss">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="cn">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="regenschreiber">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="teilgebiet">
      <editWidget type="ValueRelation">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="AllowMulti"/>
            <Option value="false" type="bool" name="AllowNull"/>
            <Option value="" type="QString" name="Description"/>
            <Option value="" type="QString" name="FilterExpression"/>
            <Option value="tgnam" type="QString" name="Key"/>
            <Option value="Teilgebiete_786fa926_704f_4cb1_bc67_eb8571f2f6c0" type="QString" name="Layer"/>
            <Option value="Teilgebiete" type="QString" name="LayerName"/>
            <Option value="spatialite" type="QString" name="LayerProviderName"/>
            <Option value="dbname='itwh.sqlite' table=&quot;teilgebiete&quot; (geom)" type="QString" name="LayerSource"/>
            <Option value="1" type="int" name="NofColumns"/>
            <Option value="false" type="bool" name="OrderByValue"/>
            <Option value="false" type="bool" name="UseCompleter"/>
            <Option value="tgnam" type="QString" name="Value"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="kommentar">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="createdat">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" type="bool" name="IsMultiline"/>
            <Option value="false" type="bool" name="UseHtml"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="pk"/>
    <alias index="1" name="Name" field="gebnam"/>
    <alias index="2" name="Schacht" field="schnam"/>
    <alias index="3" name="" field="hoeheob"/>
    <alias index="4" name="" field="hoeheun"/>
    <alias index="5" name="Fließweg" field="fliessweg"/>
    <alias index="6" name="Basisabfluss" field="basisabfluss"/>
    <alias index="7" name="CN" field="cn"/>
    <alias index="8" name="Regenschreiber" field="regenschreiber"/>
    <alias index="9" name="Teilgebiet" field="teilgebiet"/>
    <alias index="10" name="Kommentar" field="kommentar"/>
    <alias index="11" name="bearbeitet" field="createdat"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" expression="" field="pk"/>
    <default applyOnUpdate="0" expression="" field="gebnam"/>
    <default applyOnUpdate="0" expression="" field="schnam"/>
    <default applyOnUpdate="0" expression="" field="hoeheob"/>
    <default applyOnUpdate="0" expression="" field="hoeheun"/>
    <default applyOnUpdate="0" expression="" field="fliessweg"/>
    <default applyOnUpdate="0" expression="" field="basisabfluss"/>
    <default applyOnUpdate="0" expression="" field="cn"/>
    <default applyOnUpdate="0" expression="" field="regenschreiber"/>
    <default applyOnUpdate="0" expression="" field="teilgebiet"/>
    <default applyOnUpdate="0" expression="" field="kommentar"/>
    <default applyOnUpdate="0" expression=" format_date( now(), 'yyyy-MM-dd HH:mm:ss')" field="createdat"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" constraints="3" unique_strength="2" field="pk" notnull_strength="2"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="gebnam" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="schnam" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="hoeheob" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="hoeheun" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="fliessweg" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="basisabfluss" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="cn" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="regenschreiber" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="teilgebiet" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="kommentar" notnull_strength="0"/>
    <constraint exp_strength="0" constraints="0" unique_strength="0" field="createdat" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="pk"/>
    <constraint exp="" desc="" field="gebnam"/>
    <constraint exp="" desc="" field="schnam"/>
    <constraint exp="" desc="" field="hoeheob"/>
    <constraint exp="" desc="" field="hoeheun"/>
    <constraint exp="" desc="" field="fliessweg"/>
    <constraint exp="" desc="" field="basisabfluss"/>
    <constraint exp="" desc="" field="cn"/>
    <constraint exp="" desc="" field="regenschreiber"/>
    <constraint exp="" desc="" field="teilgebiet"/>
    <constraint exp="" desc="" field="kommentar"/>
    <constraint exp="" desc="" field="createdat"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column type="field" width="-1" hidden="0" name="pk"/>
      <column type="field" width="-1" hidden="0" name="gebnam"/>
      <column type="field" width="-1" hidden="0" name="schnam"/>
      <column type="field" width="-1" hidden="0" name="hoeheob"/>
      <column type="field" width="-1" hidden="0" name="hoeheun"/>
      <column type="field" width="-1" hidden="0" name="fliessweg"/>
      <column type="field" width="-1" hidden="0" name="basisabfluss"/>
      <column type="field" width="-1" hidden="0" name="cn"/>
      <column type="field" width="-1" hidden="0" name="regenschreiber"/>
      <column type="field" width="-1" hidden="0" name="teilgebiet"/>
      <column type="field" width="-1" hidden="0" name="kommentar"/>
      <column type="field" width="-1" hidden="0" name="createdat"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>uifilelayout</editorlayout>
  <editable>
    <field name="basisabfluss" editable="1"/>
    <field name="cn" editable="1"/>
    <field name="createdat" editable="1"/>
    <field name="fliessweg" editable="1"/>
    <field name="gebnam" editable="1"/>
    <field name="hoeheob" editable="1"/>
    <field name="hoeheun" editable="1"/>
    <field name="kommentar" editable="1"/>
    <field name="pk" editable="1"/>
    <field name="regenschreiber" editable="1"/>
    <field name="schnam" editable="1"/>
    <field name="teilgebiet" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="basisabfluss"/>
    <field labelOnTop="0" name="cn"/>
    <field labelOnTop="0" name="createdat"/>
    <field labelOnTop="0" name="fliessweg"/>
    <field labelOnTop="0" name="gebnam"/>
    <field labelOnTop="0" name="hoeheob"/>
    <field labelOnTop="0" name="hoeheun"/>
    <field labelOnTop="0" name="kommentar"/>
    <field labelOnTop="0" name="pk"/>
    <field labelOnTop="0" name="regenschreiber"/>
    <field labelOnTop="0" name="schnam"/>
    <field labelOnTop="0" name="teilgebiet"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="basisabfluss"/>
    <field reuseLastValue="0" name="cn"/>
    <field reuseLastValue="0" name="createdat"/>
    <field reuseLastValue="0" name="fliessweg"/>
    <field reuseLastValue="0" name="gebnam"/>
    <field reuseLastValue="0" name="hoeheob"/>
    <field reuseLastValue="0" name="hoeheun"/>
    <field reuseLastValue="0" name="kommentar"/>
    <field reuseLastValue="0" name="pk"/>
    <field reuseLastValue="0" name="regenschreiber"/>
    <field reuseLastValue="0" name="schnam"/>
    <field reuseLastValue="0" name="teilgebiet"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"gebnam"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
